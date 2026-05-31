# Project Backlog & Issues (GitHub-Style)

This document serves as the project's backlog and issue tracker. It tracks future performance optimizations, features, and documents recently resolved bugs in a structured format.

---

## 🚀 Future Performance Optimizations & Features

### [Feature] Introduce Transposition Table for State Caching #1
- **Labels**: `enhancement`, `performance`, `WIP`
- **Description**: 
  Currently, shallower lookahead dives and searches perform redundant evaluations on identical or symmetrical grid states. 
- **Proposed Solution**:
  - Implement a hash table (Transposition Table) with a rolling hash (e.g., Zobrist Hashing) for the grid states.
  - Store search depth, evaluation bounds, and classification (e.g., invalid/valid branches, solution counts) in the table.
  - Query the table at the beginning of `tree_search` and `do_l_ahead_dive` to immediately return cached results if the current depth/bounds are compatible.
- **Benefits**:
  - Eliminates exponential search space growth on symmetric/overlapping paths.
  - Makes shallow lookahead searches extremely fast and highly effective.

---

### [Performance] Cache and Reuse Node Orderings to Avoid Redundant Rescoring #2
- **Labels**: `performance`, `refactoring`
- **Description**:
  In `node_selection.c`, `try_get_best_transition` iterates through every single cell in the grid ($S^2$), checks if it is empty, and then loops through all values ($N$) in `set_best_val` to score candidate cell-value pairs. This results in $O(S^2 \times N)$ calculations *at every single search node*, even though the vast majority of the grid remains unchanged between parent and child nodes.
- **Proposed Solution**:
  - Maintain a persistent priority list of candidate cell-value transitions.
  - Instead of rebuilding the transition list from scratch, update only the affected row, column, and cell of the last set value.
  - Reuse the existing ordered list to select the next best transition in $O(1)$ time.
- **Benefits**:
  - Drastically reduces CPU cycles spent in `try_get_best_transition` and `score_transition_full`.
  - Massive speedup on larger grids (7x7, 8x8, 9x9) where transition evaluations dominate the search time.

---

## 🐛 Resolved Bugs

### [Bug] Garbage values printed when outputting solutions #3
- **Labels**: `bug`, `resolved`
- **Description**:
  `main.c` occasionally outputted grids filled with uninitialized stack memory/garbage values.
- **Root Cause**:
  `tree_search` unconditionally called `handle_leaf_node` at the end of the function, which treated internal search nodes as completed solutions and incremented `solutions_found`. This caused the stored solutions array index to go out of bounds of actual found solutions, causing `main.c` to read uninitialized memory blocks in the `solutions` array.
- **Fix**:
  Restricted the end-of-function leaf node processing to terminal states:
  ```c
  if (has_reached_terminal_state(puzzle->cur_node))
  {
      recursive_sols = handle_leaf_node(puzzle);
      update_sol_info(&recursive_sols, &node_sols);
  }
  ```

---

### [Bug] Ineffective lookahead dive pruning #4
- **Labels**: `bug`, `resolved`
- **Description**:
  Lookahead dive pruning did not mark any values invalid because it always evaluated transitions as valid.
- **Root Cause**:
  In `src/lookahead_dive.c`, the return value comparison was:
  ```c
  return (local_sols.solutions_found >= 0);
  ```
  Since `solutions_found` is `unsigned long long`, it was always `>= 0`, so lookahead dive always reported finding solutions. It also triggered a compiler error under `-Wall -Wextra -Werror` (`-Werror=type-limits`).
- **Fix**:
  Corrected the comparison to check for greater than 0 solutions:
  ```c
  return (local_sols.solutions_found > 0);
  ```

---

### [Bug] Uninitialized pruning state & redundant negative check #5
- **Labels**: `bug`, `resolved`
- **Description**:
  The project failed to compile due to compiler warnings treated as errors (`-Werror=maybe-uninitialized` and `-Werror=type-limits`).
- **Root Cause**:
  - `t_node_pruning_state pruning;` in `prune_node` was allocated but not initialized. `keep_pruning` occasionally returned `1` early without writing to its fields, causing uninitialized memory reads.
  - `skip_pruning` checked `if (unset_threshold < 0)` on the unsigned `unset_threshold` variable, which was dead code and triggered compiler errors.
- **Fix**:
  - Zero-initialized `pruning` upon declaration: `pruning = (t_node_pruning_state){0};`.
  - Removed the redundant `< 0` check.
