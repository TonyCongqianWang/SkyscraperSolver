# Skyscraper Solver - Agent Methodology

This document outlines the workflows, style compliance standards, verification procedures, and regression-checking guidelines established during the `refactor-pruning-node-strategies` optimization track.

---

## 🛡️ 1. Code Style & Linter Compliance (42 Norminette)

All source code (`src/*.c`, `src/*.h`) must strictly comply with the **42 Norminette** rules. If any modification is made, run the following linter command:

```bash
norminette src/*.c src/*.h
```

### Critical Rules to Remember:
1. **No Mixed Tabs/Spaces**: All indentation must be done exclusively using tabs.
2. **Function Length**: No function may exceed **25 lines** of executable code. If a function is too long, decompose it into smaller static helper functions.
3. **Parameter Limit**: No function may accept more than **4 arguments**. If a function requires more context, package arguments inside a helper struct (see `t_hidden_param` in `src/prune_gac_hidden.h`).
4. **Function Limit per File**: No source file may contain more than **5 functions**. Files must be modularized accordingly (e.g. splitting GAC into `prune_gac.c`, `prune_gac_domain.c`, `prune_gac_naked.c`, and `prune_gac_hidden.c`).
5. **Variable Declarations**: 
   - All variable declarations must be at the very top of a function block.
   - Declarations cannot be initialized at definition (except in global scopes/constants).
   - Align variable names at the same column index using tabs (column 21 is the standard for this project).

---

## 🔍 2. Correctness & Solution Count Verification

Because Skyscraper puzzles can have multiple valid grid solutions depending on clue configurations, comparing solution grids directly across versions is prone to false positives. Correctness must be verified by comparing **exhaustive solution counts** under the `-s 0` flag.

### Verification Workflow:
1. **Preserve Baseline**: Compile the reference version from the `main` branch and copy it as `skyscraper_solver_main` in the workspace root.
2. **Run Consistency Script**:
   We have created a parallel consistency check script at `python_scripts/verify_consistency.py`. Run it on a benchmark set:

   ```bash
   python3 python_scripts/verify_consistency.py benchmark_sets/benchmarkSet7.txt
   ```

3. **How It Works**:
   - The script runs both `./skyscraper_solver` (refactored) and `./skyscraper_solver_main` (baseline) concurrently on every instance.
   - It parses `Solutions found: <count>` and asserts that the count matches exactly.
   - **Important**: Always verify on Size 7 benchmark sets for fast, exhaustive checking. Size 8 sets are computationally expensive for `-s 0` and should only be verified on smaller subsets (e.g., `benchmarkSet8_subset10.txt`).

---

## ⚡ 3. Performance & Node Count Benchmarking

To measure how changes affect solver search speed and search space compression:

> [!WARNING]
> Do NOT use `--binary` or `--set` arguments with `run_benchmark.py`. They are unrecognized and will fail.
> Always specify the solver binary command using the `-c` flag and pass the benchmark set text file path as the final positional argument.

1. Run the benchmark tool against the random subset of size 7 (`benchmarkSet7_rand100.txt`) or the full suite:

   ```bash
   python3 python_scripts/run_benchmark.py -c ./skyscraper_solver benchmark_sets/benchmarkSet7_rand100.txt
   ```

2. Compare the **Total Nodes Visited** and **Total Time** metrics against the baseline version (`./skyscraper_solver_main`).

---

## 📈 4. Strategy Patterns & Pruning Hyperparameters

- **Configuration Routing**: Exposed via [src/strategy_routing.c](file:///Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/refactor-pruning-node-strategies/src/strategy_routing.c). Modify this file to adjust when GAC and Lookahead Pruning are applied.
- **Root vs. Deep Pruning**:
  - GAC is computationally expensive. It is best applied fully at the **root node** (depth 0) to shrink initial domains, and selectively (`is_selective = 1`) at shallow deep nodes (e.g., when `unset_ratio > 0.7`).
  - Caching and reuse of node selection orderings are routed in `select_node_select_config`.
