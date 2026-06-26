# Skyscraper Solver - Resuming Context & Technical Reference

This document contains deep technical references on the solver's algorithmic state tracking, type-safety abstractions, and implementation details for developer reference.

---

## ⏱️ 1. Search Activity & Progress Tracking

The solver uses a progress counter to track search activity and dynamically determine when to trigger pruning routines.

### Progress Metrics
* **Search Activity (`progress_counter`)**: Measured in arbitrary units of search progress. Inside `src/grid_manipulation.c`, it is incremented:
  * `+10` when a cell value is successfully assigned (`set_grid_val`).
  * `+1` when a cell value is marked invalid (`set_value_invalid`).
* **Period Escalation**: In each pruning strategy routing module (e.g., `prune_root.c`), the solver tracks when the last pruning routine ran using `node->last_prog[tier]`. A pruning routine at a given tier is executed only if:
  $$\text{node->progress\_counter} > \text{node->last\_prog[tier]} + \text{tier\_period}$$
* **Tiered Periods**:
  * **Light**: Runs with a period of `period / 2` (frequent, lightweight lookahead).
  * **Medium**: Runs with a period of `period` (standard lookahead).
  * **Heavy**: Runs with a period of `period * 2` (occasional, exhaustive lookahead/GAC sweeps).

### Period Scaling (Search Depth Decay)
To prevent the solver from wasting CPU cycles running heavy lookahead steps on highly determined states, the base period is dynamically scaled.
As the search goes deeper (fewer empty cells), the `unset_ratio` drops:
$$\text{unset\_ratio} = \frac{\text{num\_unset}}{\text{squared\_size}}$$
The base period for a node is scaled by:
$$\text{period} \propto \frac{1}{\text{unset\_ratio}^4}$$
Near the root, `unset_ratio` is high, keeping the period small (frequent pruning). Near leaf nodes, `unset_ratio` approaches 0, scaling the period towards infinity (deactivating lookahead and GAC).

---

## 🧬 2. Selectivity & Early Exit Logic

Selectivity controls how aggressively lookahead and GAC filters are applied during a solve.

### Selectivity Levels
1. **`SELECTIVITY_NONE`**: Lookahead checks all candidate cell values for all empty cells. GAC and Check Constraints run fully.
2. **`SELECTIVITY_VALUE_SET`**: Lookahead only runs if values have been successfully assigned since the last prune.
3. **`SELECTIVITY_ANY_CHANGE`**: Lookahead runs if values have been assigned or marked invalid since the last prune.

### Early Exit Guards
At the entry points of `prune_gac`, `prune_check_constr`, and `prune_lookahead`, the solver checks the changed and invalid flags:
* `node->rows_changed_since_prune` / `node->cols_changed_since_prune` (set when values are assigned).
* `node->rows_invalid_since_prune` / `node->cols_invalid_since_prune` (set when values are marked invalid).

If the current selectivity level's conditions are not met, the routines exit immediately. This avoids scanning unchanged row/column states, preventing CPU overhead in deep search branches.

---

## 🛡️ 3. Type Safety Abstractions

To prevent compiler warnings and clarify integer scale requirements, the codebase defines explicit type aliases:
* **`t_prune_prog`**: A 64-bit integer (`unsigned long long`) tracking the progression of search activity.
* **`t_sol_count`**: A 64-bit integer tracking the number of solutions found.
* **`t_node_count`**: A 64-bit integer tracking the total search nodes visited during search.

---

## ⚡ 4. Scripting & Tooling Reference

* **Consistency Checking**: The verification script `python_scripts/verify_consistency.py` validates that new solver implementations match baseline solution counts. Usually it should be run with NO extra arguments. A shortcut for that is to use make with target `test`.

* **Benchmarking**: Use `python_scripts/run_benchmark.py` to evaluate execution times. The solver binary is specified via `-c` and the benchmark set path is passed as the final argument:
  ```bash
  python python_scripts/run_benchmark.py -c ./skyscraper_solver benchmark_sets/benchmarkSet7.txt
  ```
* **Scratch Space**: Place all temporary analysis scripts, experimental results, and transient outputs under the `scratch/` directory, which is excluded from git tracking.
