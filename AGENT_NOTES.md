# Skyscraper Solver - Resuming Context & Deep Technical Notes

If you are a newly spawned agent inheriting this workspace, read this document carefully. It explains the critical bugs, algorithmic mechanics, and platform-specific behaviors that were addressed in the `v08` performance optimization cycle.

---

## 🐞 1. Key Logic Bugs Resolved

### A. The Inverted Skip-Pruning Logic Error
* **The Bug**: Inside `skip_pruning` (`src/node_pruning.c`), the progress check was originally inverted:
  ```c
  if (node->progress_counter >= unset_threshold)
      return (1); // Skipped pruning when progress was above the threshold!
  ```
  This logic skipped pruning precisely when the solver was making massive progress (which is the most beneficial time to prune) and executed lookahead diving when no progress was being made.
* **The Fix**: Corrected to:
  ```c
  if (node->progress_counter < unset_threshold)
      return (1); // Skip pruning when progress is below threshold
  ```
* **Critical Context**: `progress_counter` acts as a measure of search activity. It is incremented in `src/grid_manipulation.c` by `+10` on `set_grid_val` (successful assignment) and `+1` on `set_value_invalid` (invalidation of a value for a cell).

### B. Pruning Call Placement in Backtracking Block
* **The Bug**: Pruning was previously called redundantly at the beginning of `search_step` (`src/tree_search.c`).
* **The Fix**: Placed `prune_node` at the bottom of `search_step` immediately inside the backtrack invalidation block:
  ```c
  if (update_sol_info(&recursive_sols, node_sols)
      || !check_sol_target(node_sols, puzzle->cur_node)
      || recursive_sols.min_nunset == puzzle->squared_size)
  {
      set_value_invalid(puzzle->cur_node, next.cell_idx, next.cell_val);
      prune_node(puzzle); // Called here to propagate failures cleanly
  }
  ```
* **Why This Matters**: Triggers lookahead pruning precisely when branches collapse. If the collapse is minor, `progress_counter` increments slowly, and the corrected `skip_pruning` naturally treats it as a fast no-op. If major branches collapse, full lookahead is triggered to propagate the failures.

---

## ⚙️ 2. Pruning Mechanics & Hyperparameters

### A. Skip Pruning Decay via `unset_ratio`
* **Mechanic**: The base pruning period `period` is dynamically divided by `unset_ratio`:
  $$\text{unset\_ratio} = \frac{\text{num\_unset}}{\text{squared\_size}}$$
  $$\text{period} = \frac{\text{base\_period}}{\text{unset\_ratio}}$$
* **Behavior**: At the start of the solve, `unset_ratio` is `1.0` (period remains at base). Near the leaf nodes, `unset_ratio` approaches `0.0`, causing the scaled `period` to expand toward infinity. This naturally decays lookahead frequency and avoids expensive dives in highly determined deep nodes.

### B. Progress-Based Reiteration
* **Mechanic**: Inside `prune_node`, lookahead reiterates only if progress exceeds a threshold:
  $$\text{progress} = \text{progress\_counter}_{\text{post}} - \text{progress\_counter}_{\text{pre}} \ge g\_prune\_reiterate\_threshold$$
* **Tuning Results**: 
  Grid search on Size 7 subsets proved that a reiteration threshold $T = 3$ is mathematically optimal (visiting **684,366 nodes** vs. **798,665 nodes** with $T = 2$). 
  * **Rationale**: Lookahead passes are expensive ($O(S^2 \times N)$). Reiterating for fewer than 3 invalidations incurs more lookahead overhead than the search space compression saves.

---

## 🛡️ 3. Strong Type Safety & Variable Alignment (42 Norm)

To clean up unwieldy `unsigned long long` uses, we introduced three typedefs in `src/puzzle_structs.h`:
* `t_prune_prog`: Tracks node pruning progress.
* `t_sol_count`: Tracks maximum solutions, solutions found, and solution indices.
* `t_node_count`: Tracks overall nodes visited.

### Variable Alignment under Norminette
Norminette requires all variable declarations in a block to align their names at the exact same column using tabs. 
* **The Challenge**: Shorter types like `int` and longer types like `const t_prune_prog` must have their variables aligned.
* **The Solution**: Align names at column 21.
  ```c
  const double		g_min_unset_r_prune = 0.4;     // const double (12 chars) + 2 tabs
  const int			g_max_p_depth_shallow = 1;     // const int (9 chars) + 3 tabs
  const t_prune_prog	g_prune_reiterate_threshold = 3; // const t_prune_prog (18 chars) + 1 tab
  ```

---

## ⚡ 4. Concurrent Tuning & Compiler Race Conditions (Windows)

The tuning blueprint script [python_scripts/examples/tune_parameters.py](python_scripts/examples/tune_parameters.py) runs a 48-combination grid search concurrently across 8 threads. If you modify or run it:

1. **Avoid `os.listdir` Race Conditions**:
   Do **not** list `src/` dynamically in the worker threads. Since workers concurrently write `node_pruning_worker_X.c` files, listing `src/` dynamically will cause a thread to capture another thread's temporary file and attempt to compile it, leading to duplicate definitions or compilation crashes when that file is deleted.
   * **Implementation**: Gather baseline `.c` files once in the master thread (filtering out any `node_pruning_worker_` prefixes) and pass that static list to the threads.
2. **Binary Locking**:
   Windows locks running executables. Compile to isolated worker names: `skyscraper_solver_worker_{id}.exe`.
3. **Environment cleanup**:
   Always run a pre-tuning cleanup to remove stale `node_pruning_worker_*.c` and `skyscraper_solver_worker_*.exe` files left over from previous interrupted runs.
