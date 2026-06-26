# Skyscraper Solver - Development & Optimization Methodology

This document outlines the software engineering methodologies, correctness verification workflows, benchmarking protocols, and parameter-tuning strategies for the Skyscraper Solver.

---

## ⚙️ 1. Solver Architecture & Pruning Paradigm

The Skyscraper Solver is a backtracking constraint satisfaction solver optimized through lookahead techniques, generalized arc consistency (GAC), and dynamic programming (DP) constraint checks.

### Pruning Escalation Scheme
To balance pruning strength and CPU overhead, the solver organizes pruning routines into three primary tiers:
1. **Light**: Minimum overhead. Primarily runs lookahead under a relaxed selectivity condition (`SELECTIVITY_VALUE_SET`).
2. **Medium**: Moderate strength. Performs lookahead under a broader selectivity condition (`SELECTIVITY_ANY_CHANGE`).
3. **Heavy**: High strength. Performs exhaustive lookahead without selectivity filters (`SELECTIVITY_NONE`).

### Selective Early Exits
Pruning routines must dynamically inspect the grid state before running expensive operations:
* If selectivity is `SELECTIVITY_VALUE_SET` and no cell values have changed since the last pass, the solver must immediately return.
* If selectivity is `SELECTIVITY_ANY_CHANGE` and no cell values have changed or been invalidated, the solver must immediately return.

### Dynamic Activation of Pruning Strategies
Pruning routines should be dynamically activated based on the node's position in the search tree (depth) and current grid density (`unset_ratio`):
* **Generalized Arc Consistency (GAC)**: Extremely effective when the search space is broad (shallower nodes/high unset ratios). At deeper nodes, standard backtracking and domain reduction are faster than full GAC sweeps.
* **DP Check Constraints**: Best utilized in narrow grid density windows (e.g., `unset_ratio` between `0.3` and `0.6`). When the board is too open (high unset ratios), it rarely prunes; when too constrained (low unset ratios), simpler checks suffice.

---

## 🔍 2. Correctness & Solution Verification

Refactoring pruning strategies or solver internals carries a high risk of introducing correctness bugs (e.g., pruning valid branches). Correctness must be verified before profiling performance.

### Verification Principles
1. **Exhaustive Enumeration (`-s 0`)**: Comparing single solutions found is insufficient because multiple valid solutions can exist for a given clue set, and search order changes will produce different grids. Correctness is verified by confirming that the total number of solutions found is identical to the baseline.
2. **Puzzle Size Constraints**:
   * **Size 7**: Fast enough to run exhaustive enumeration (`-s 0`) on all instances.
   * **Size 8**: Exhaustive enumeration is feasible on easy sets (e.g., 50 instances). Avoid running `-s 0` on hard or random Size 8 sets.
   * **Size 9**: Exhaustive enumeration is computationally infeasible. Correctness must be verified using single-solution search (`-s 1`).

---

## 📊 3. Benchmarking & Evaluation Guidelines

Performance optimization of constraint solvers requires careful benchmarking due to search-space variance.

### Search Space & Execution Variance
* **Single Solution Search (`-s 1`)**: High variance. The time to find the first solution is heavily dependent on search order and early branch decisions. A minor configuration change can cause the solver to either stumble upon the solution immediately or get trapped in a large sub-tree.
* **Aggregated Statistics**: Never rely on a single instance. Run benchmarks over representing test sets (e.g., 35-100 instances) and track:
  * **Total Wall Time**: The actual end-to-end user latency.
  * **Mean & Median Instance Time**: Identifies whether speedups are uniform or driven by outliers.
  * **Mean & Median Nodes Visited**: A timing-independent metric of search-space compression.
* **Difficulty Distribution**: Evaluate configurations against multiple sets (Easy, Medium, Hard, and Infeasible). A configuration that excels at Easy puzzles (due to low overhead) may cause a catastrophic search-space explosion on Hard puzzles.

---

## 📈 4. Parameter Tuning & Optimization Strategy

Tuning parameters (periods, unset ratios, selectivity levels) requires a disciplined multi-phase filtering approach to avoid overfitting.

### The Overfitting Trap
When tuning pruning configurations, optimizing strictly against single-solution search (`-s 1`) on small or easy puzzles is dangerous. Because lookahead is computationally heavy, the optimizer will greedily disable lookahead and GAC to minimize overhead on easy instances. However, when applied to hard or larger puzzles, this lack of pruning leads to search-space explosions.
* **Remedy**: Use exhaustive search (`-s 0`) during the early tuning phases on Size 7 and Size 8 instances to evaluate actual search-tree reduction, then validate against Size 9 single-solution searches.

### Multi-Phase Filtering Workflow
1. **Phase 1: High-Throughput Node-Count Filtering**: Evaluate parameter configurations on small datasets using `-s 0` and filter based on *node counts* (which are deterministic and noise-free).
2. **Phase 2: Deduplication & Calibration**: Calibrate unique survivor configurations on a mixed set (including Size 9 instances under `-s 1`) with high timeouts to discard configurations prone to search traps.
3. **Phase 3: Timing-Based Evaluation**: Run the top survivors on larger datasets to identify configurations that balance search space reduction with CPU execution time.

---

## 🛡️ 5. Development and Environment Constraints

### Code Style Compliance (42 Norminette)
Production releases should respect standard formatting conventions to maintain readability:
* **Function Limits**: Functions should be concise (typically under 25 lines) and focus on a single task.
* **Argument Limits**: Keep functions under 4 parameters; pass structured configuration objects (e.g., `t_prune_routine_cfg`) if more context is needed.
* **File Separation**: Group related logic into modular source files (e.g., separating GAC routines, lookahead logic, and check constraints).
* *Note*: During active exploration and tuning phases, strict compliance can be temporarily relaxed to accelerate iterations.

### Platform-Specific Execution (Windows / MinGW)
* **File Locking**: Windows locks running executables. If the solver crashes, ensure the process is terminated (e.g., `Stop-Process` or `taskkill`) to allow recompilation.
* **Environment Paths**: Ensure compiler toolchains (such as GCC/MinGW) are added to the active environment path inside your shell session when compiling.
