# Work calibration

## Current counter and output schema

The single supported solver counter schema is `WORK_COUNTERS v1`, with
48 fixed-count / variable-volume event counters. The counter names in
`src/work_instrumentation.h`, `src/work_instrumentation_report.c`, and
`python_scripts/calibrate_work.py` must agree exactly. The normal native
solver does not emit these counters. The instrumented solver includes no
wall-clock timers unless explicitly compiled with `WORK_MICRO_TIMING`.

The sole supported compact model schema is `v1`, with format
`skyscraper-work-model` version 1. The previous pooled fit is invalid after the new instrumentation. Run
calibration before using the work tuning objective; it writes a new
`scratch/work_calibration.model.json` and corresponding collinearity
report. The work tuning objective loads that generated model in **seconds**
and fails if it is missing. There is no compatibility projection or
fallback to obsolete fitted coefficients.
The measured **time + nodes** objective remains separately available.

## Run calibration

```sh
python3 python_scripts/calibrate_work.py
# Reproduce the puzzle choice, train/validation splits, and perturbations:
python3 python_scripts/calibrate_work.py --seed 123456
```

When `--seed` is omitted, the script generates a fresh 64-bit random seed
and prints it. The seed is stored in the detailed report with the puzzle
identities and all configurations. With the same seed, dataset files and
code, puzzle selection, splits and parameter variants are reproducible.
Native runtime measurements and CPU microtimings naturally remain subject
to machine scheduling and load.

Default sampling draws 512 symmetry-distinct puzzles of each size 7, 8
and 9 from the corresponding **active SPSA training datasets**, across
their entire files:

- `puzzle_bank/spsa_datasets/le7_train.txt` (size-7 entries)
- `puzzle_bank/spsa_datasets/size8_train.txt`
- `puzzle_bank/spsa_datasets/size9_train.txt`

The sampler uses a seeded hash-priority reservoir to avoid file-order bias.
A separate seeded, puzzle-identity-level 25% holdout is selected within
each size. Every configuration of a puzzle stays on the same split, and
nested training-only splits select ridge and contrast penalties.
Independent SPSA validation datasets are used only for the final
micro-timing verification, not for fitting or regularization selection.

The default configurations consist of a baseline and **six random
antithetic SPSA-style direction pairs per size**, simultaneously varying
all six cache/score parameters for that size. Each direction draws signed,
seeded perturbations of 25% to 75% around the configured defaults.
There are 13 configurations per size, 19,968 observations in total.
`--no-perturb` disables parameter perturbations. A fixed `--seed`
repeats the exact perturbation choices.

Size 7 runs full enumeration by default; sizes 8 and 9 run first-solution
search. `--max-solutions` overrides this. Native time is measured 9
times per observation by default, instrumentation 3 times, and section
timing once. Use `--puzzles-per-size`, `--native-repeats` and
`--instrumented-repeats` to control the workload.

## Numerical fitting and cost splits

Work features with near-duplicate counter patterns are merged before
regression. Nonnegative RMS-scaled ridge regression with optional
within-puzzle contrast weighting fits the merged feature coefficients.
The target runtimes are converted from seconds to **milliseconds inside
the numerical optimizer**, improving the scale of its absolute convergence
threshold. The resulting intercept, per-count coefficients, predictions
and every exported field remain in **seconds**. This internal conversion
does not change the units of tuning losses or the meaning of ridge alpha.

Once the pooled regression has been fitted, section timings from the
initial solver runs and a controlled C microbenchmark of **each original
counter in the known collinear groups** are combined to estimate
relative operation costs. Those timing-derived ratios distribute the
single fitted merged-group coefficient algebraically among its original
members, preserving total training-set group contribution. No refitting
occurs. Unmeasured members are an error, not an arbitrary equal-weight
fallback. A separate evaluation reports the allocated model's held-out
ranking and prediction drift.

The controlled microbenchmark uses actual C operations, repeated under
`-O2 -flto` to amortize timer overhead. The independent section-timing
check uses SPSA validation puzzles and never changes coefficients.
Timing disagreements and their source measurements remain visible.

## Output artifacts

```text
scratch/work_calibration.raw.jsonl
scratch/work_calibration.json
scratch/work_calibration.model.json
scratch/work_calibration.collinearity.json
scratch/work_calibration.micro.json
```

The first two are detailed records for analysis. The compact model contains
the deployable pooled per-counter coefficients, intercept, training
provenance, holdout scores and hyperparameters. The collinearity file
contains original merged groups and timing-derived allocations. The micro
file independently verifies timing ratios on validation puzzles.

To export the compact files again from the detailed report:

```sh
python3 python_scripts/work_model_export.py \
    --input scratch/work_calibration.json
```

For a cheap pipeline check without reliable statistical conclusions:

```sh
python3 python_scripts/calibrate_work.py --seed 42 \
    --puzzles-per-size 4 --native-repeats 3 \
    --instrumented-repeats 2 --no-perturb --no-micro-verify
```

The standalone microcheck can be invoked with:

```sh
python3 python_scripts/work_micro_probe.py \
    --model scratch/work_calibration.model.json \
    --collinearity scratch/work_calibration.collinearity.json
```

The key optimization metric is **clear within-puzzle ranking accuracy**:
compare configurations of the same puzzle only when their measured
runtime difference exceeds the maximum of 50 microseconds and twice
the estimated combined standard error of the native timing medians.
Absolute R² alone does not measure ranking ability. The primary fit
is pooled; size-specific fits are diagnostics.

**Scope:** calibration is trained on size-7 enumeration and size-8/9
first-solution runs. Size-8 enumeration remains an out-of-distribution
tuning mode until separately validated.

## Work-counter terminology and constraint-checking coverage

`dp_candidate_check` counts previous-maximum state iterations in the **current
prefix/suffix DP candidate-feasibility checker**; it is unrelated to the
removed generalized arc consistency algorithm. `cache_build_candidate`
counts candidate values examined during cache construction (the candidate
may also generate a transition). `provisional_solution_rollback` counts
a reversal of a speculative solution registration, **not** ordinary search
backtracking. These label-only changes preserve existing fitted coefficients.

`assignment` counts one event regardless of puzzle size, whereas its
candidate invalidation attempts and the ordinary clue-bound checks that
follow are size dependent. Successful domain invalidations are already
counted separately, but ordinary `check_active_constr` line iterations and
bounds updates are currently **not counted directly**. Adding those work
features requires a new regression calibration and cannot be represented by
simply renaming the existing deployed coefficients.

## Recalibration required after adding work counters

The 15 new counters capture clue-bound checking calls and actual per-line
positions, unset-cell bounds processing, dirty-entry dequeue/enqueue,
failed-or-successful domain invalidation attempts, cell-bound skips,
cache-build cell traversal, candidate selection and resumption scans,
next-valid-value probes, pruning line traversal, and DP prefix/suffix/prune
candidate loop probes. The existing successful `domain_invalidation` counter
remains distinct, and `assignment` remains one fixed event.

All previous 33-counter coefficients were fitted without these operations,
so they must **not** be reused as a tuning cost model. Full recalibration
produces the replacement model at `scratch/work_calibration.model.json`.
The new counters are counted in instrumentation without modifying solver
logic. The controlled microbenchmark must also independently time every
member of any new collinear group before coefficient allocation can complete;
calibration fails closed when this is not possible.
