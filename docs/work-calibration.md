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
No pip packages are required.

```sh
python3 python_scripts/calibrate_work.py \
    --limit-per-dataset 8 --native-repeats 3 \
    --output scratch/work_calibration.json
```

For experiments including individual cache-period and lookahead-score
perturbations, add `--perturb`. Use `--dataset PATH` repeatedly to choose
datasets, `--max-solutions 0` for enumeration, and
`--limit-per-dataset` to restrict cost. This script compiles isolated variants
in a temporary directory without modifying tracked solver sources. It performs
two instrumented runs per puzzle for deterministic-counter checks and repeated
native runs for each puzzle/configuration. Mismatching solution/node counts
fail immediately. Default dataset files cover <=7, 8 and 9.

The JSON artifact stores dataset paths and SHA256 hashes, puzzle line numbers,
clues and optional grid, compiler/build options, git commit, parameter variants,
native timing samples, count vectors, nonnegative fitted coefficients and
held-out prediction/ranking diagnostics. The fit uses scaled coordinate descent
and a nonnegative intercept; no third-party linear algebra package is needed.

The split holds out entire puzzle identities. Ranking comparisons are evaluated
within a puzzle across parameter configurations. The summary also reports
size/mode subsets. Ranking accuracy is `null` when no comparable pairs exist;
run with `--perturb` and larger datasets before trusting it. The script does
**not** modify SPSA objectives or claim the surrogate is validated by default.
Once validated, use estimated seconds with an explicitly chosen shifted-log
normalization and freeze the v1 coefficients for a tuning campaign. Keep final
native baseline/optimized comparisons with uninstrumented binaries.

Counters capture distinct work units: cache metadata/pair copies; candidate
checks and moves; insertion-sort comparisons and shifts; score and blend
evaluations; propagation updates/GAC checks; assignments and invalidations;
node copies, lookahead scans, solution copies and rollbacks; plus setup.
A single action may legitimately touch separate units (e.g. checking and
moving), but no summary counter duplicates them. This is a cost model, not a
cycle-accurate profiler; inspect quality on held-out data before tuning.
