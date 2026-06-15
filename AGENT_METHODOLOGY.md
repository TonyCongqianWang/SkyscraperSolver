# Skyscraper Solver - Agent Methodology

This document outlines the workflows, style compliance standards, verification procedures, and hyperparameter tuning guidelines established during the `refactor-pruning-node-strategies` optimization track.

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
4. **Function Limit per File**: Source files must contain no more than **5 functions**. Files must be modularized accordingly (e.g. splitting GAC into `prune_gac.c`, `prune_gac_domain.c`, `prune_gac_naked.c`, and `prune_gac_hidden.c`).
5. **Variable Declarations**: 
   - All variable declarations must be at the very top of a function block.
   - Declarations cannot be initialized at definition (except in global scopes/constants).
   - Align variable names at the same column index using tabs (column 21 is the standard for this project).

---

## 🔍 2. Correctness & Solution Count Verification

Because Skyscraper puzzles can have multiple valid grid solutions depending on clue configurations, comparing solution grids directly across versions is prone to false positives. Correctness must be verified by comparing **exhaustive solution counts** under the `-s 0` flag.

### Automated Verification Workflow:
We have created a parallel consistency check script at `python_scripts/verify_consistency.py`. 

1. **Default Verification**: Run the script without arguments to automatically run the quick verification suites on Size 7 and Size 8 sets against expected solutions:
   ```bash
   python3 python_scripts/verify_consistency.py
   ```
2. **Checking Specific Benchmark Files**:
   ```bash
   python3 python_scripts/verify_consistency.py benchmark_sets/benchmarkSet7.txt
   ```
3. **Correctness Conventions**:
   - **Size 7**: Always verify using the `-s 0` flag (exhaustive search) as size 7 instances are quick.
   - **Size 8**: Only use `-s 0` on easy sets (e.g. `benchmarkSet8_easy50.txt`). Never run `-s 0` on random or hard size-8 instances as it is computationally prohibitive.
   - **Size 9**: Never use `-s 0` for verification; verify using standard `-s 1` (single solution) only.

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

## 📈 4. Hyperparameter Optimization (HPO) Tuning Gauntlet

To optimize pruning strategy routing hyperparameters efficiently without compiling thousands of binaries, we compile a single binary with conditional environment variable loading (`-DG_PRUNE_NO_ENV=0`) and execute a multi-phase gauntlet script.

> [!IMPORTANT]
> **Exhaustive Search Requirement**: To avoid overfitting, hyperparameter tuning on size-7 and size-8 instances must always use **full enumeration (`-s 0`)** instead of single-solution search (`-s 1`). 
> - *Why?* If S8 instances are evaluated using single-solution search (`-s 1`), the search is too shallow and lookahead pruning overhead dominates. The HPO will greedily select passive parameters that minimize/disable lookahead pruning. This causes a catastrophic explosion of search nodes (up to 8.3x) when the selected configuration is deployed on harder datasets.

### Workflow & Concepts:
1. **High-Throughput Pre-Filtering (Phase 1)**:
   - Evaluate all generated configuration combinations on cheap tiny sets (100 S7 + 50 S8). This is timing-noise independent and runs very fast.
   - **Exhaustive Search**: S7 and S8 instances must be evaluated under `-s 0`.
   - **Stratified Filtering**: Filter survivors by keeping the top 20% of configurations by node count within each GAC threshold group. This preserves parameter diversity across GAC thresholds.
2. **Post-Phase 1 Calibration Deduplication**:
   - Run deduplication only on Phase 1 survivors using 5 calibration instances (1 size-7 with `-s 0`, 1 size-8 with `-s 0`, 3 hard size-9 with `-s 1`). This avoids executing heavy size-9 instances on thousands of poor configurations.
   - **High Timeout Safeguard**: Use a 10.0-second timeout for calibration solver runs to prevent temporary CPU noise from falsely timing out and discarding valid configurations.
3. **Gauntlet Skip Logic**:
   - If the deduplicated unique survivor count drops below 2,000, skip Phase 1b (tiny sets time filter) entirely and route survivors directly to Phase 2 (small sets time filter) to optimize execution time.
4. **Timing-Based Filtering (Phases 2-4)**:
   - Progressively evaluate survivor configurations on larger sets (`S7_SMALL`, `S8_MEDIUM`, `S7_FULL`) to refine timing signals and report the optimal winners. Always preserve the `-s 0` flag for size 7 and size 8.

