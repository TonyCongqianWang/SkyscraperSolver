# Deterministic solver work counters (issue #72)

Normal builds compile empty `work_*` functions, while `make instrumented`
builds a separate `skyscraper_solver_work` using `-DWORK_INSTRUMENTED`.
Only `src/work_instrumentation*.c` contain instrumentation preprocessing
conditionals; solver code calls the same ordinary ABI in both modes.
`-flto` can eliminate calls to empty functions in normal builds (inspect
assembly to confirm for a given toolchain; this is an optimization, not a C
language guarantee). No counters are stored in puzzle/node structs.

Work counters are emitted in a single `WORK_COUNTERS v1` record for each
successfully parsed solve, including standard input mode. They start before
solver initialization, and are counted through completion of the solve; printing
and cleanup are outside the scope. The v1 schema is defined in
`src/work_instrumentation.h`, with corresponding names in the report source.

## Calibrate from a fresh clone

Requirements: Python 3.9+, GCC (or an LTO-capable C compiler), and `git`.
No pip packages are required. Default usage:

```sh
python3 python_scripts/calibrate_work.py --output scratch/work_calibration.json
```

**Default workload:** 128 symmetry-distinct puzzles for **each** size 7, 8,
and 9, drawn from `benchmarkSet7_easy500.txt`, `benchmarkSet8.txt`, and
`benchmarkSet9.txt`. Size 7 runs **full enumeration** (`-s 0`);
sizes 8 and 9 find the first solution (`-s 1`). These modes are recorded
per puzzle. The script fails if the default datasets cannot supply 128
distinct puzzles of each size.

Parameter perturbations are **enabled by default**: 12 variants per size
(two perturbations of six cache/score parameters), plus baseline.
Each variant only runs against its matching size; that makes 13
configurations per size, **4,992 puzzle/configuration observations** total.
For every observation there are two instrumented runs (cross-checked for
identical counters, solution counts and nodes) and three independent native
wall-time measurements. Total raw executions are **24,960**. This is a
deliberately substantial benchmark, not a quick smoke test.

With a fixed, per-size 75%/25% puzzle-identity split, the default is
1,248 training and 416 validation observations **per size** (96 training
and 32 held-out puzzles, each with 13 configurations): **3,744 training**,
**1,248 validation** overall. Rotations/reflections of the same clues
are grouped under a canonical puzzle identity before selection or splitting.

Options: `--puzzles-per-size N` for smaller smoke runs; `--no-perturb`
to omit configuration changes; repeat `--dataset PATH` for custom input.
The `--max-solutions N` option overrides size-specific defaults (e.g.,
`--max-solutions 0` for enumeration of all sizes). The `--timeout`,
`--native-repeats`, `--seed`, and `--validation-fraction` options
control execution and splitting.

The script compiles instrumented and native binaries in a temporary
directory without modifying tracked source files. For each run it writes
a **raw execution record immediately** to
`scratch/work_calibration.raw.jsonl`, including the dataset hash, canonical
puzzle ID, configuration and parameters, size/mode, repeat index, elapsed
time, solutions/nodes and unaggregated counters (instrumented runs only).
This file survives an interrupted run. On successful completion it writes
`scratch/work_calibration.json`, containing the raw runs, counter vectors,
all native timings/medians, SHA256 dataset hashes, build provenance, per-fit
coefficients, work predictions and held-out diagnostics.

## Four fits and collinearity handling

The script fits models on **size 7**, **size 8**, **size 9**, and the
**pooled sizes** separately. All four report independent nonnegative
coefficients, intercepts, per-puzzle ranking diagnostics, held-out MAE/R²,
counter feature groups and numerical-rank information.
The JSON also compares pooled vs size-specific held-out predictions.
The held-out rows are not used for grouping or fitting.

On *training rows only*, columns with zero variance are excluded from
coefficient identification (but remain in raw output). A centered
Pearson correlation of absolute value >=0.995 triggers pairwise grouping;
approximately multivariate-dependent columns are identified through
twice-reorthogonalized Gram–Schmidt using a 0.001 relative residual
threshold. Correlated features are merged as **sums of original raw work
counts**, and the fitted coefficient is shared across that group.
The output records all original names, group membership, correlation
values, merge decisions, constant counters and effective ranks before
and after grouping. Thresholds can be changed with
`--correlation-threshold` and `--dependency-tolerance`.

**Important limitation:** summing columns assumes equal provisional cost
per work unit within a group. It is not a measurement of their relative
costs, and can be inaccurate for negatively correlated or intrinsically
different operations. We deliberately retain raw counters so later
microbenchmarks can establish cost ratios and replace these provisional
groups. Rank is an approximate numerical diagnostic (Gram–Schmidt), not
an SVD condition number, and near dependencies can be threshold-sensitive.

The surrogate is **not** automatically used for SPSA tuning; first
inspect held-out ranking quality, agreement among the four fits, and
periodic uninstrumented native comparisons. Freeze the schema and fitted
weights for each tuning campaign.


Counters capture distinct work units: cache metadata/pair copies; candidate
checks and moves; insertion-sort comparisons and shifts; score and blend
evaluations; propagation updates/GAC checks; assignments and invalidations;
node copies, lookahead scans, solution copies and rollbacks; plus setup.
A single action may legitimately touch separate units (e.g. checking and
moving), but no summary counter duplicates them. This is a cost model, not a
cycle-accurate profiler; inspect quality on held-out data before tuning.
