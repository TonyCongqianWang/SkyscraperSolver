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

**Default workload:** 512 symmetry-distinct puzzles for **each** size 7, 8,
and 9, sampled exclusively from the **active SPSA training datasets**:
`puzzle_bank/spsa_datasets/le7_train.txt`,
`puzzle_bank/spsa_datasets/size8_train.txt`, and
`puzzle_bank/spsa_datasets/size9_train.txt`. The le7 file contains mixed
sizes 5–7; this calibration selects size 7 from it. A deterministic
seeded hash-priority sample spans each **entire** training file rather than
taking the first 512 lines (the SPSA datasets may be ordered by difficulty).
Size 7 runs **full enumeration** (`-s 0`); sizes 8 and 9 find the first
solution (`-s 1`). These modes are recorded per puzzle. The script fails
if the default datasets cannot supply 512 distinct puzzles of each size.

**Calibration holdout:** the 25% holdout is carved from these sampled
SPSA **training** puzzles, using symmetry-canonical puzzle identities.
The separate SPSA `*_val.txt` files are **not** used for coefficient
fitting, feature grouping, or the calibration holdout; they remain untouched
for independent SPSA validation. This keeps calibration aligned with the
actual SPSA training distribution without leaking official validation data.

Parameter perturbations are **enabled by default**: 12 variants per size
(two perturbations of six cache/score parameters), plus baseline.
Each variant only runs against its matching size; that makes 13
configurations per size, **19,968 puzzle/configuration observations** total.
For every observation there are **three instrumented runs** (cross-checked
for identical counters, solution counts and nodes) and **nine independent
native wall-time measurements**. All calibration and held-out instances
receive the same repeat counts; there are **239,616 raw executions**.
This is a substantial benchmark, not a quick smoke test.

With a fixed, per-size 75%/25% puzzle-identity split, the default is
4,992 training and 1,664 validation observations **per size** (384 training
and 128 held-out puzzles, each with 13 configurations): **14,976 training**,
**4,992 validation** overall. Rotations/reflections of the same clues
are grouped under a canonical puzzle identity before selection or splitting.

Options: `--puzzles-per-size N` for smaller smoke runs; `--no-perturb`
to omit configuration changes; repeat `--dataset PATH` for custom input.
The `--max-solutions N` option overrides size-specific defaults (e.g.,
`--max-solutions 0` for enumeration of all sizes). The `--timeout`,
`--native-repeats`, `--instrumented-repeats`, `--seed`, and
`--validation-fraction` options control execution and splitting. For a
small smoke run use `--puzzles-per-size 4 --native-repeats 3
--instrumented-repeats 2 --no-perturb`.

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

On successful completion the script **also exports a compact pooled model** to
`scratch/work_calibration.model.json` (or `--model-output PATH`) and a
separate pooled collinearity report to
`scratch/work_calibration.collinearity.json`
(or `--collinearity-output PATH`). It has
only a versioned schema, raw-counter weights, intercept, creation timestamp,
dataset hashes, compiler/commit, selected ridge and contrast penalties, and
key held-out scores. No raw observations, individual run timings, tuning
grid, or size-specific coefficients are included. The model's coefficients
are already expanded onto the original counter names, so consumers need
only `intercept_seconds + sum(seconds_per_count[key] * counts[key])`.
Unidentifiable counters receive an explicit zero weight.

To export an already generated detailed calibration file without recalibrating:

```sh
python3 python_scripts/work_model_export.py \
    --input scratch/work_calibration.json \
    --output scratch/work_calibration.model.json \
    --collinearity-output scratch/work_calibration.collinearity.json
```

The collinearity file is intentionally **pooled-only**. It includes
counter schema and raw names, all merged groups with original member
names and provisional fitted group weights, pairwise correlations with
their Pearson coefficients, ordered merge decisions (including
multivariate dependencies), rank diagnostics before/after merging,
constant/dropped counters and the original detection thresholds.
It records the same creation timestamp and source revision as the compact
model. The goal is to identify operations whose relative physical costs
need microbenchmarking, **not** to interpret a correlation coefficient as
a measured runtime cost ratio. No size-specific fits, per-puzzle records
or full tuning grids appear in this export.

The exporter can also read a previous v1 detailed report, retaining that
original counter schema; only use models with a matching instrumented solver
counter schema. For new models this is `v1`. The loader
`work_model_export.load_compact_model` and predictor
`work_model_export.predict_seconds` validate the compact format and require
the complete raw counter set. Treat the compact file as the only
deployment/tuning artifact; keep the raw JSONL and detailed report for
reproducibility and diagnostics.

## Pooled model and size-specific diagnostics

The **pooled model is the primary model** and the only one exported for use
in tuning. The script still fits **size 7**, **size 8**, and **size 9**
independently for diagnostics, but does not export them as deployable models.
The detailed report additionally includes
`pooled_validation_by_size`, showing *the same pooled model* evaluated
separately on each puzzle size so comparisons do not confuse a size-specific
fit with a pooled prediction. The pooled fit and diagnostic models each
retain independent held-out score reports.

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

## Counter semantics: real work volumes and fixed-size copies

The instrumentation schema has changed from **v1 to v1**. Re-run the
instrumented calibration to obtain valid coefficients for the new schema.
The old v1 model must not be combined with v1 raw counters.

For variable-size operations, measure both fixed invocation overhead and
actual touched work where practical:

| Operation | Calls | Volume |
| --- | --- | --- |
| Cache entry pair copy | `cache_pair_copy_call` | `cache_pair_copy` = actual copied entries |
| Line entropy scoring | `line_score` | `line_score_value` = values scanned in entropy loop |
| DP table initialization | `dp_init_call` | `dp_init_write` = actual initialized/overwritten table slots |
| Constraint-index copy | `index_copy_call` | `index_copy_pair` = forward/reverse index pairs copied |

Each call/volume pair lets the pooled regression estimate a fixed term
plus a variable term. The old `cache_pair_copy` counter already measured
entries, and now has a separate call counter. Inner loop counters such as
`gac_check` and `propagate_dp_update` already measure actual work and
are not multiplied by another polynomial in grid size.

**Crucially,** `t_node_state`, `t_line_order` and `t_order_state`
are C structs with fixed-maximum arrays (81 grid cells, 18 lines, etc.).
Assigning one of these copies its entire fixed-size struct, *not only the
active puzzle cells*. Their `node_copy`, `line_copy`,
`cache_state_copy` and `solution_copy` counters remain simple counts.
Do not multiply them by `n*n` or `n`, which would misrepresent actual
memory traffic. The finite cost of any fixed-size copy is absorbed in
its count coefficient.

The collinearity analyzer may still merge nearly dependent call/volume
columns when the training set does not identify separate costs. The
compact export preserves the exact pooled prediction by expanding the
merged-group coefficient back onto every original counter. Keep the raw
v1 counters for later microbenchmarks to determine independent ratios.

## Ranking-focused regularization and timing uncertainty

The original fit was nonnegative least squares (NNLS), solved by coordinate
descent on normalized counter columns and with an unpenalized intercept.
The new fit uses **nonnegative ridge** with optional within-puzzle
configuration-contrast loss:

```text
min_{b>=0, w>=0}  MSE(t, b + Xw)
               + contrast_weight * mean_squared_centered_puzzle_error
               + ridge_alpha * sum(w_scaled**2)
```

Each feature is normalized by its training RMS; only coefficients are
penalized, not the intercept. The contrast term subtracts the mean target
and prediction of *each puzzle's configurations*, so that small within-puzzle
runtime changes count even when between-puzzle runtime variance dominates.

The ridge grid defaults to `0,1e-6,1e-4,1e-2` and contrast grid to
`0,1,4,16`. The selected pair is chosen by an **inner 20% puzzle-level
split within the outer training set**; the final 25% held-out set never
influences fitting or selection. On inner holdout, prefer ranking accuracy
for confident configuration pairs; if there are too few confident pairs,
minimize within-puzzle centered MAE instead. Both the full tuning grid
and the selected parameters are stored per size and for the pooled fit.
The output also records the unregularized model's held-out metrics for
direct comparison.

The original pairwise ranking accuracy (including nearly tied configurations)
is preserved. Additional diagnostics include:

- **Clear-pair ranking accuracy and coverage**: exclude comparisons whose
  measured time difference is below a noise threshold. The threshold is
  `max(minimum_delta, noise_z * hypot(SE_median_1, SE_median_2))`, using
  the standard deviation of repeated native times and a normal-approximation
  standard error for the median. Defaults: `noise_z=2` and
  `minimum_delta=0.00005` seconds.
- **Within-puzzle centered MAE and R²**: remove each puzzle's mean so
  a good between-puzzle R² cannot hide poor configuration sensitivity.
- **Macro clear-pair ranking**: average the accuracy across puzzles with
  clear differences, rather than treating every correlated pair as
  statistically independent.

Timing confidence filtering is an approximate noise diagnostic, **not**
a formal significance test. More repeats reduce measurement uncertainty,
but tiny runtimes and subprocess startup variability can still make near-tie
rankings unreliable. Compare results from the regularized and unregularized
models; there is no guarantee regularization will improve rankings.

The surrogate is **not** automatically used for SPSA tuning. Inspect
held-out rank accuracy (particularly *clear* pairs), pooled performance per size,
and periodic uninstrumented comparisons before using coefficients in SPSA.
Size-8 calibration continues to measure first-solution mode by default;
the SPSA training objective also evaluates enumeration, which needs
separate validation before extrapolating the surrogate across modes.



Counters capture distinct work units: cache metadata/pair copies; candidate
checks and moves; insertion-sort comparisons and shifts; score and blend
evaluations; propagation updates/GAC checks; assignments and invalidations;
node copies, lookahead scans, solution copies and rollbacks; plus setup.
A single action may legitimately touch separate units (e.g. checking and
moving), but no summary counter duplicates them. This is a cost model, not a
cycle-accurate profiler; inspect quality on held-out data before tuning.
