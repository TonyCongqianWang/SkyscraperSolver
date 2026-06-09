# Plan: Strategy Pattern for Pruning and Node Selection

This document outlines the master architecture to introduce a Strategy Pattern for both pruning and node selection. This abstraction allows the solver to dynamically select different algorithmic strategies at different stages of the search tree, maximizing performance and efficiency.

---

## 1. Sub-Plans

The details of the strategies and their implementations are split into:
- **[Pruning Strategy Plan](file:///Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/refactor-pruning-node-strategies/TODO_PLAN_PRUNING.md)**: Lookahead dive (complete vs. selective), Generalized Arc Consistency (GAC) for naked/hidden tuples, and selective row/column tracking.
- **[Node Selection Strategy Plan](file:///Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/refactor-pruning-node-strategies/TODO_PLAN_NODE_SELECTION.md)**: Scoring families (Branching, MRV, Progress), ordering cache/reuse, and sorted list retrievals.

---

## 2. File Layout

To maintain strong modularity and conform to the 42 Norm (under 25 lines per function, 5 variables per function, 4 parameters), the codebase will be laid out as follows:

| File | Type | Purpose |
| --- | --- | --- |
| `src/strategy_config.h` | Header | Config structs, strategy enums, and presets. |
| `src/strategy_routing.h` / `.c` | Core | Dynamic strategy selector functions (`select_prune_config`, `select_node_select_config`). |
| `src/prune_lookahead.h` / `.c` | Module | Depth/budget lookahead dives, selective pruning filters. |
| `src/prune_gac.h` / `.c` | Module | Generalized Arc Consistency solver (naked/hidden tuples). |
| `src/node_selection_score.h` / `.c` | Module | Score computations for Branching, MRV, and Progress. |
| `src/node_selection_cache.h` / `.c` | Module | Caching, sorting, and O(1) transition retrieval. |
| `Makefile` | Build | Handles compilation rules dynamically. |

---

## 3. Integration Points

### A. Tree Search Core (`src/tree_search.c`)
- In `tree_search(t_puzzle *puzzle)`:
  - Inside the main while-loop, fetch the node selection configuration via `select_node_select_config(puzzle, &config)`.
  - Pass the configuration to `try_get_best_transition_strat(puzzle, &next, &config)`.
- In `prune_node(t_puzzle *puzzle)` (`src/node_pruning.c`):
  - Fetch the pruning configuration via `select_prune_config(puzzle, &config)`.
  - Delegate execution to `prune_node_strat(puzzle, &config)`.

### B. Grid Manipulation (`src/grid_manipulation.c`)
- Add bitmask updates inside `set_grid_val`:
  - `state->rows_changed_since_prune |= (1 << (cell_idx / state->size));`
  - `state->cols_changed_since_prune |= (1 << (cell_idx % state->size));`

### C. Structures Definition (`src/puzzle_structs.h`)
- Add `rows_changed_since_prune`, `cols_changed_since_prune`, and `order_cache` to `t_node_state`.

---

## 4. Verification Plan

1. **Compilation Check**:
   Compile with strict flags using the Makefile:
   ```bash
   make
   ```
2. **Correctness Validation**:
   Run the full size 7 benchmark suite. Verify that solution counts match the baseline perfectly:
   `python3 python_scripts/run_benchmark.py --binary ./skyscraper_solver`
3. **Performance Profiling**:
   Evaluate changes on size 8 and size 9 benchmark instances. Verify that total node visits and CPU time are reduced.
4. **Norminette Check**:
   Run `norminette` on all newly added and modified files to guarantee 100% compliance.
