# Walkthrough: Solver Code Refactoring & Norminette Compliance

This walkthrough documents the cleanups, architectural refactoring, and 42 Norminette compliance achievements performed on the Skyscraper Solver codebase.

---

## 📁 File & Function Renamings
To eliminate uninformative or misspelled file names and conform to proper naming standards:
* **`src/print_utlilty.c` / `src/print_utility.h`** $\rightarrow$ [print_io.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/print_io.c) / [print_io.h](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/print_io.h) (fixed spelling of "utility" and renamed to `io` for clarity).
* **`src/prune_check_constr_utils.c`** $\rightarrow$ [prune_check_constr_evaluate.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_check_constr_evaluate.c) (renamed to reflect its responsibility of evaluating constraint DP tables).
* **`src/node_selection_utils.c`** $\rightarrow$ [node_selection_transition.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/node_selection_transition.c) (renamed to represent its focus on transition scoring/evaluation).
* **`src/node_selection_cache_helper.c`** $\rightarrow$ [node_selection_cache_update.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/node_selection_cache_update.c) (renamed to describe the caching updates logic).

---

## 🗂️ Grouping Pruning Strategy Files
Strategy routing files have been renamed to group them next to each other in file list outputs:
* `src/prune_root.[ch]` $\rightarrow$ [prune_strat_root.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_root.c) / [prune_strat_root.h](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_root.h)
* `src/prune_shallow.[ch]` $\rightarrow$ [prune_strat_shallow.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_shallow.c) / [prune_strat_shallow.h](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_shallow.h)
* `src/prune_medium.[ch]` $\rightarrow$ [prune_strat_medium.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_medium.c) / [prune_strat_medium.h](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_medium.h)
* `src/prune_deep.[ch]` $\rightarrow$ [prune_strat_deep.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_deep.c) / [prune_strat_deep.h](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_deep.h)
* `src/prune_initial.[ch]` $\rightarrow$ [prune_strat_initial.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_initial.c) / [prune_strat_initial.h](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_strat_initial.h)

---

## 🔍 Shared Selectivity Module
A brand new, clean selectivity module was introduced to extract early-exit logic that checks whether pruning should proceed and filters active rows/columns:
* [selectivity.h](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/selectivity.h) and [selectivity.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/selectivity.c) contain:
  * `should_exit_selectivity`: Determines if selectivity mode is set and no progress has been made, enabling instant early return.
  * `should_process_row`: Determines if a specific row has seen recent changes (for `SELECTIVITY_ANY_CHANGE` and `SELECTIVITY_VALUE_SET`).
  * `should_process_col`: Determines if a specific column has seen recent changes.

---

## 🛠️ Restructured Loop Logic
1. **Separated GAC Loops**:
   In [prune_gac.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_gac.c), the mixed loop that iterated over both row and column indices was split into two separate, clean loops (one for rows and one for columns), integrating the shared selectivity helpers.
2. **Separated Check Constraints Loops**:
   In [prune_check_constr.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_check_constr.c), we separated row checks and column checks into distinct helper functions `check_constr_rows` and `check_constr_cols`.

---

## ⚙️ Static Global Parameters
Tunable base coefficients and thresholds were moved to the top of their respective strategy files as static global constants prefixed with `g_`:
* `g_max_depth_coeff`
* `g_unset_ratio_root_shallow`
* `g_unset_ratio_other`
* `g_constr_range_start`
* `g_constr_range_end`

---

## 🧼 100% Norminette Style Compliance
The codebase was brought to **100% compliance** with the 42 Norminette tool:
* **Function Length**: Split functions exceeding 25 lines (e.g. `pruning_routines.c::run_pruning_routine`, `prune_check_constr.c::prune_check_constr`, `prune_lookahead.c::run_lookahead_loop`) into smaller, focused static helpers.
* **File Function Limit**: Distributed Check Constraints functionality across [prune_check_constr_evaluate.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_check_constr_evaluate.c) and [prune_check_constr_propagate.c](file:///C:/Users/TonyC/Documents/Projects/repos/SkyscraperSolver/src/prune_check_constr_propagate.c) to adhere to the 5-function limit per file.
* **Line Length**: Wrapped lines exceeding 80 characters (e.g. in `node_selection_eval.c`, `tree_search_step.c`, and `pruning_routines.c`).
* **Variable Declarations**: Aligned variable declarations using tabs and ensured declaration of variables occurs only at the beginning of functions.

---

## 📈 Verification & Testing
* **Compilation**: `make` runs cleanly with no warnings or errors using GCC.
* **Norminette Scan**: The scanner reports **`OK!`** for every `.c` and `.h` file under the `src/` directory.
* **Consistency Check**: `verify_consistency.py` ran against the refactored solver executable `skyscraper_solver.exe` on all Size 7 and Size 8 default benchmarks, achieving **100% matching solution counts** (0 mismatches, 0 crashes).
