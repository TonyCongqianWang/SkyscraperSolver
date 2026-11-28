# Work calibration

## Current counter and output schema

The single supported solver counter schema is `WORK_COUNTERS v1`, with
48 fixed-count / variable-volume event counters. The counter names in
`src/work_instrumentation.h`, `src/work_instrumentation_report.c`, and
`python_scripts/calibrate_work.py` must agree exactly. The normal native
solver does not emit these counters. The instrumented solver includes no
wall-clock timers unless explicitly compiled with `WORK_MICRO_TIMING`.

The sole supported compact model schema is `v1`, with format
`skyscraper-work-model` version 1. A completed, verified 48-counter pooled model is now committed at
`scratch/work_calibration.model.json`, the default SPSA tuning path.
It is based on the fully resolved November 24 calibration and is usable
immediately for tuning on this branch. A new full calibration overwrites
that file locally when requested; it does not need to be rerun before
the initial tuning run. The previous 33-counter fit is obsolete. The work tuning objective loads that generated model in **seconds**
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

Default sampling draws 6,000 symmetry-distinct puzzles of each size 7, 8
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

Each distinct puzzle now receives **one independently seeded antithetic
plus/minus pair**. Every SPSA-active parameter is perturbed, including the
shared strategy parameters and the math parameters relevant to that size;
the other-size parameters remain at their defaults. The direction is drawn
from an ellipsoid in normalized SPSA coordinates and scaled by each
parameter's SPSA perturbation scale. Its marginal scale is approximately
`4 * c` (`c=0.03` by default). The high-dimensional sampling includes a
`sqrt(d)` factor so individual changes do not collapse to zero as the
number of active parameters grows; legal ranges and linked constraints
are projected using the same rules as SPSA.

This gives **36,000 distinct puzzle–configuration observations**
(18,000 puzzles × two parameter configurations) by default.
Each observation receives two native runtime measurements and exactly one
counter-producing execution. For every antithetic pair, a seed-dependent
hash selects one member for section timing; the other uses plain
instrumentation. Both supply the full 48 work counters. Section timing
therefore covers exactly half the observations without sacrificing any
counter coverage or fitting observations.
The default budget is **72,000 native, 18,000 section-timed and 18,000 plain
instrumented executions** (108,000 solver invocations total, excluding the
independent validation and controlled microbenchmark). Native timing spreads
are saved as a simple stability proxy. Native solution and node counts must
agree for every observation. Extra plain runs on timed observations, if
requested, must match all 48 counters.
A preflight log prints the exact budget and fails clearly when any requested
puzzle size lacks enough unique puzzles rather than silently reducing
coverage. Each required binary is compiled only once; a temporary generated
runtime override constructor applies parameter values through environment
variables without editing the repository's C source files. The default calibration
model remains unchanged until a new calibration is run. `--perturb`,
`--perturb-radius`, `--no-perturb`, and `--seed` configure or reproduce
these choices.

Size 7 runs full enumeration by default; sizes 8 and 9 run first-solution
search. `--max-solutions` overrides this. Use `--puzzles-per-size`,
`--native-repeats` (minimum 2) and `--instrumented-repeats` (default 0.5)
to control the workload. With section timing enabled, rates below 0.5
are raised to 0.5 to guarantee counter coverage. The default 0.5 uses
one plain and one section-timed execution per pair. A rate of 1 adds a
plain parity check to each timed observation; higher rates add repeats.
Fractional extra runs are hash-ranked independently within each size,
rounding the total plain budget to the nearest observation (half up).
With `--no-perturb`, half of each size's single observations are timed
(rounding up), with the rest covered by plain instrumentation; rounding
the plain budget may add a parity check. Any missing counters or parity
mismatch is fatal. With `--no-section-timing`, plain instrumentation
supplies all counters, so rates below 1 are raised to 1 and logged.
Section-timing diagnostics use only timed observations; regression and
ranking diagnostics use all observations.

## Interruptions, resuming, and timeouts

The assigned counter-producing execution establishes the checkpoint: the
section-timed build for its half of the pair, otherwise the plain
instrumented build. Static CPU budgets are **2 seconds for size 7, 2 for
size 8, and 5 for size 9**; override with `--cpu-timeout-size7`,
`--cpu-timeout-size8`, or `--cpu-timeout-size9`. The outer DFS checks
the clock only at main-node advances after nested probes return. A
checkpoint can overshoot the budget by the work of one main node.
If interrupted, the solver emits `SEARCH_STATUS timeout`, main and total
node counts, all counters, and completed section samples. Both native
repeats and optional plain parity runs replay that exact main-node
checkpoint with no CPU-clock checks. Completed solves replay without
a node limit. Ordinary solver usage has no timeout unless explicitly
configured by environment variables `SOLVER_CPU_TIMEOUT` or
`SOLVER_MAIN_NODE_LIMIT` (mutually exclusive).

Matched partial prefixes contribute to coefficient fitting and
collinearity, but only completed solves contribute to configuration
ranking and within-puzzle contrast terms. Regression error metrics
include partial prefixes and explicitly report their count; complete-only
MAE is also reported. Independent section validation uses the same
size-specific CPU budgets. SPSA's training policy is unchanged.
The emergency wall-clock subprocess timeout defaults to 60 seconds
(`--timeout SECONDS`); if exceeded, calibration stops and preserves
the journal rather than fabricating a partial result. Progress logs
show per-size cumulative runtime by mode every 16 puzzles and identify
invocations still running after 10 seconds. These CPU budgets are not
a strict whole-job wall-clock guarantee.

Every completed solver invocation is appended immediately to
`scratch/work_calibration.raw.jsonl`, including runs from partially completed
puzzles. Existing journals are protected from accidental overwriting.
If calibration stops, preserve the JSONL file and resume using the **original
seed and all original sampling/benchmark options**:

```sh
python3 python_scripts/calibrate_work.py --seed 123456 --resume
```

Resume validates puzzle identities, dataset hashes, parameter perturbations,
the deterministic per-observation parity schedule, run counts and
work-counter schemas before reusing records; completed runs are not rerun.
New raw records include the seed, repeat settings, section-timing mode
and sampling versions, CPU budgets and checkpoint policy so changes are
rejected. The original leader status and checkpoint are preserved and
validated against all replays; earlier journals without checkpoint metadata
require the original revision. Journals from the prior
all-observation timing schedule with a recorded run plan cannot be resumed
under the new schedule. Preserve them and use the original revision to
resume, or choose a separate `--output` path for a new calibration. For a new calibration using the same output file, specify
`--fresh` to intentionally discard the existing raw journal. Never use
`--fresh` when you wish to recover an interrupted run.

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
occurs. Unmeasured or unstable members are recorded as warnings, not used for
arbitrary equal-weight fallback, and not a reason to discard any calibration
results. The detailed report preserves the pooled regression, solver timings
and counter measurements. The compact model is still written, but an
unresolved group has `null` per-counter coefficients and is tagged
`status: incomplete` / `usable_for_tuning: false`; tuning refuses it.
The collinearity export identifies each unresolved group and missing
member. Already resolved allocations remain in the report.

Independent SPSA validation *still runs* when timing cost allocation is
unresolved. The validator uses an in-memory algebraic projection of the
single fitted **pooled regression**, and records those validation outcomes
alongside observed CPU timing ratios; it explicitly withholds only
conclusions about unresolved individual cost ratios. This projected
predictor is solely for diagnostics, never substituted into the exported
tuning model. A separate evaluation reports the allocated model's held-out
ranking and prediction drift only if every split is resolved.

The controlled microbenchmark covers the previously merged groups plus
additional genuine operations including `lookahead_scan`, `resume_scan`,
`rescore_scan`, `base_score`, `rel_entropy_value`, and representative
node/solution copies, score blending, provisional rollback, successful
domain invalidation, and line scoring. Missing or unidentifiable counters remain visible in
the 48-counter coverage report instead of being silently assumed timed.
The `counter_diagnostics` reason distinguishes `not_benchmarked`,
`insufficient_timing_evidence`, and `unstable`. These are diagnostic
states, not calibration-fatal errors.

The controlled microbenchmark uses actual C operations, repeated under
`-O2 -flto` to amortize timer overhead. The independent section-timing
check uses SPSA validation puzzles and never changes coefficients.
Timing disagreements and their source measurements remain visible.
The controlled harness now also measures real successful `assignment`
operations. It constructs a consistent seven-by-seven state and resets
that state before each operation. The paired control performs the same
18 invalidations and two dirty-constraint enqueues, but no assignment;
the instrumented build checks these exact counter increments for both
paths. The reported assignment-only cost is the difference between the
full assignment time and this matched nested-work control. Both gross
and control times are retained in the raw benchmark records. The
difference is an approximate residual, not a guarantee of independently
identifying an instruction-level exclusive cost: near-zero or negative
estimates remain visible, are flagged as unstable, and never silently
converted to positive coefficients.

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
When individual allocations remain unresolved, the micro report is still
produced with `completed_with_unresolved_allocation`, using independently
sampled validation puzzles and the pooled predictor. The report preserves
measured ratios and marks unsupported split comparisons `unresolved`.
An actual validation execution error produces a warning and a `failed` report,
without deleting the calibration outputs. Explicit
`--no-micro-verify` writes a `skipped_by_request` report.

To export the compact files again from the detailed report:

```sh
python3 python_scripts/work_model_export.py \
    --input scratch/work_calibration.json
```

For a cheap pipeline check without reliable statistical conclusions:

```sh
python3 python_scripts/calibrate_work.py --seed 42 \
    --puzzles-per-size 4 --native-repeats 3 \
    --instrumented-repeats 0.5 --no-perturb --no-micro-verify
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

### Adaptive controlled timing and zero-weight groups

A zero merged coefficient is allocated exactly to all-zero member weights, without inventing timing ratios; missing timing diagnostics remain recorded. Positive groups still require stable independent evidence. Controlled DP initialization varies actual table size; suffix DP timing varies candidate density at fixed scan volume, with instrumented shadow checks of counts. The constraint checker also has a zero-cell call measurement. `--micro-repeats` starts each independent timing batch and `--micro-max-repeats` (default 4000000) bounds doubling retries for insufficient or unstable evidence in positive merged groups. Accepted estimates retain their first complete independent batch; raw attempts are recorded. The regression is never refitted during allocation.
