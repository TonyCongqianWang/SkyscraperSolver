# Agent Methodology: Hyperparameter Optimization (HPO) for Skyscraper Solver

This document outlines the stochastic, multi-task hyperparameter optimization (HPO) methodology developed to optimize the Skyscraper Solver's pruning constants.

---

## 📐 1. Optimization Setup

The solver exposes **29 parameters** across depth levels (Root, Shallow, Medium, Deep) and routing boundaries. These parameters control:
* **GAC Thresholds** (`g_gac_unset_threshold`)
* **Constraint Ranges** (`g_constr_min_unset`, `g_constr_max_unset`)
* **Period Coefficients** (`g_period_base`, `g_period_coef1`, `g_period_coef2` for quadratic period scaling)

---

## 🛠️ 2. SPSA Tuning Framework with Capping

We utilize **Simultaneous Perturbation Stochastic Approximation (SPSA)** to navigate the 29-dimensional parameter space.

### The Problem of Timeout-Induced Gradient Explosion
During SPSA, if one parameter perturbation (e.g. $\theta + c_k \Delta$) hits a search trap and times out (taking 10s), while the other ($\theta - c_k \Delta$) solves normally (taking 0.5s), the difference in loss is massive. Since the SPSA gradient estimate is:
$$g_i = \frac{L(\theta + c_k \Delta) - L(\theta - c_k \Delta)}{2 c_k \Delta_i}$$
This huge loss difference produces a **giant gradient spike**. In subsequent update steps, this spike instantly throws the parameter to its boundaries (typically `0.5` or `0.0`), disabling pruning and causing massive regressions.

### The Solution: Step Size Capping (Gradient Clipping)
To guarantee optimization stability, we implement **step size capping** on the parameter update step:
```python
max_step = 0.02
theta_next = []
for i in range(len(theta)):
    step_i = ak * grad[i]
    # Cap the maximum parameter update step to prevent boundary clipping
    step_c = max(-max_step, min(max_step, step_i))
    val = max(0.0, min(1.0, theta[i] - step_c))
    theta_next.append(val)
theta = theta_next
```
Capping the step size to `0.02` per iteration ensures that parameter adjustments are smooth and noise-robust, forcing the optimizer to find a stable local basin rather than getting thrown to extreme boundaries by a single timeout.

---

## ⚙️ 3. Execution & Process Management on Windows

Running high-throughput benchmarks on Windows introduces process-creation bottlenecks and pipe-read lockups:
1. **Windows Defender Suspension**: Spawning processes rapidly in parallel can trigger anti-virus heuristic suspensions. Keep parallel workers limited (e.g., `max_workers = 4`).
2. **Double-Timeout Pipe Safeguard**: Python's `subprocess.run(..., timeout=timeout)` can hang indefinitely on Windows if `proc.kill()` is called but pipe handles remain open. Instead, use `subprocess.Popen` with a double-timeout communication wrapper:
   ```python
   proc = subprocess.Popen(...)
   try:
       stdout, stderr = proc.communicate(timeout=timeout)
   except subprocess.TimeoutExpired:
       proc.kill()
       try:
           stdout, stderr = proc.communicate(timeout=0.5)
       except Exception:
           pass
   ```

---

## 📊 4. Multi-Task Loss Weighting

To balance solver performance across multiple puzzle sizes and difficulties without overfitting, we use stochastically drawn training batches at each iteration and score them using a weighted multi-task loss function:
$$\text{Loss}_{\text{total}} = 0.2 \times \text{Loss}_{S7} + 0.5 \times \text{Loss}_{S8} + 1.0 \times \text{Loss}_{S9\_calib} + 8.0 \times \text{Loss}_{S9\_harder}$$

* The S7 and S8 losses ensure that optimizing for harder puzzles does not cause regressions on easy/medium enumerations.
* The 8.0x multiplier on `S9_harder` forces SPSA to prioritize subtree compression on hard puzzles.
* Individual times ($t_i$) and node counts ($n_i$) are aggregated using **Shifted Geometric Mean (SGM)** to minimize the impact of outlier runtimes.
