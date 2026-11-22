# Draft: work-based tuning and experimental micro probes

The bundled compact model in `python_scripts/models/work_calibration.model.json`
is the user-provided pooled v2 model (trained on 14,976 observations; validated
on 4,992). The adjacent collinearity file records its merged counter groups.

## Tuning

From a clean clone:

```sh
./setup_and_tune.sh --size 8 --iterations 100
./setup_and_tune.sh --sweep --mode math8 --no-compare
```

The wrapper builds two environment-overridable solver variants: the normal
native binary (used for post-tuning wall-time comparisons) and a dedicated
instrumented work binary (used for training). Both tuners default to the
same pooled `v2` calibration file, validate counter names and schema, and
use deterministic work predictions in **seconds**. The measured time + nodes objective remains a fully supported alternative,
selected explicitly:

```sh
./setup_and_tune.sh --size 8 --nodes-time --iterations 100
./setup_and_tune.sh --sweep --mode math8 --nodes-time
```

`--work-model PATH` can point to another compatible compact model.
The loss definitions, shifts, references and mode policies reside in
`python_scripts/tuning_objective.py`. The measured time + nodes objective retains its own established
mixing weights for SPSA and sweep. In work mode, SPSA's two existing
optimizer gradient streams receive the *same work loss*, so their average
is mathematically the single work gradient, not a mixture with nodes.

Timeouts keep the 40-second PAR4 penalty, not the surrogate intercept.
Missing, malformed or mismatched counter records raise errors rather than
receiving an artificially cheap work score. Native comparisons remain
un-instrumented and report true time and nodes. Each run records the
calibration SHA256 in metadata.

**Model limitations:** It was trained for full enumeration of size 7, and
first-solution search for sizes 8 and 9. Size 8 enumeration and sizes 5–6
within the mixed le7 dataset are **out of distribution**. The size-8 pooled
clear-pair held-out ranking was 60.0%; don't deploy as a new permanent
SPSA objective without confirming actual native batch rankings, especially
on these solve modes.

## Additional v3 counters and model compatibility

Four previously unrepresented operations are now counted in the solver:
`rescore_scan` counts every cached score rescan,
`resume_scan` counts resume-index linear-search comparisons,
`rel_entropy_value` counts the active values evaluated by relative
constraint-entropy calculations, and `domain_scan` counts candidate
values checked while constructing a constraint domain. The instrumentation
record is now `WORK_COUNTERS v3`. This improves physical coverage but
**does not establish the reason for size-8 ranking errors** without rerunning
and inspecting the new fit. The previously committed pooled `v2` model
is temporarily projected onto the original counters for tuning, explicitly
ignoring the new four work features; a new `v3` calibration should replace it.

## Section timing plausibility during calibration

Normal calibration now builds a **third, separately timed instrumented**
binary for each configuration and executes each puzzle once more. This is
enabled by default:

```sh
python3 python_scripts/calibrate_work.py
# Smoke test: normal plus micro timing, no parameter perturbation
python3 python_scripts/calibrate_work.py --puzzles-per-size 4 --no-perturb \
  --native-repeats 3 --instrumented-repeats 2
# Turn off the extra timed run when only refitting is needed
python3 python_scripts/calibrate_work.py --no-section-timing
```

Its `section_timing_plausibility` report contains **train** and
**held-out validation** results, using the same already-fitted pooled
coefficients in both. The per-section results include Pearson correlation
between measured section CPU totals and predicted costs, measured/predicted
ratios, sample counts, and how many observations were unresolved because
timings were zero or there were too few samples. The report also evaluates
the pooled model's timing plausibility separately on held-out size-7,
size-8, and size-9 puzzles, making it easier to isolate the size-8 gap. The overall
`plausibility_score` is the average of measurable per-section correlations,
with explicit coverage. If none are measurable it is `null` (not zero).
The report also records the fraction of the fitted (non-intercept)
counter cost represented by the six timed call/volume features; a high
correlation on a small fraction does **not** validate the whole model.

**Automatic independent check:** once the four fitted models and the compact
pooled export have been written, calibration automatically invokes the
standalone micro-timing verification on up to **32 symmetry-distinct puzzles
per size from the SPSA `*_val.txt` datasets** (not the calibration training
or held-out observations). It builds a fresh timed baseline executable and
saves `scratch/work_calibration.micro.json`. This contains the new pooled
fit's timing plausibility overall and separately by size, plus a
`split_verification` comparison of timing-derived call/volume cost ratios
to the pooled coefficients, identifying consistent, disagreeing and
unresolved splits. The default 2× ratio tolerance is a heuristic, not a
statistical test. The independent validation data never influence the fit.
Disable the extra check with `--no-micro-verify` or reduce its size with
`--micro-puzzles-per-size N`.

To rerun the verification for an existing v3 fit without recalibration:

```sh
python3 python_scripts/work_micro_probe.py \
  --model scratch/work_calibration.model.json \
  --collinearity scratch/work_calibration.collinearity.json \
  --puzzles-per-size 32 \
  --output scratch/work_calibration.micro.json
```

This is an independent **held-out solver-section timing experiment**, not
an isolated synthetic-loop microbenchmark. It checks whether the candidate
cost split transfers to unseen puzzles, but does not isolate the runtime
of every operation independently. It can report `unresolved` where
timed call and volume counts remain collinear, fitted costs are zero, or
samples are too short to estimate a ratio.

Each timed section additionally reports a **standalone nonnegative affine
call/volume fit**, based solely on the CPU samples (not on solver wall
times). If call counts and sampled work volumes are distinguishable, it
reports measured seconds per call, seconds per work unit, and their ratio.
If sampled features are collinear or timing is insufficient, the split is
marked unidentifiable. This lets you compare a micro-derived split with the
pooled regression's provisional equal-cost merged groups. The two measured
CPU coefficients are diagnostics and never overwrite calibration weights.

**Scope:** these checks currently cover only cache-entry copying, line
entropy scoring, and index copying. They do not establish ratios for all
merged counter groups. Timing a complete group containing nested or jointly
executed operations does not by itself identify each member's independent
cost.

For each selected package, the predicted section work is calculated from
its **actual sampled invocation count and its actual sampled volume**
using its two fitted coefficients. The timed version uses the process
CPU-time clock with nanosecond conversion. Timing begins and ends around
a sampled invocation (every 64th call) and does not influence model fitting,
merging or hyperparameter selection. The full calibration report retains
the timing records alongside the raw work observations.

The standalone script invokes the same separately compiled
`WORK_MICRO_TIMING` instrumentation, with sampled sections every 64th
cache-entry copy, line entropy score, and constraint-index copy. It uses
the provided v3 compact model, never the bundled v2 tuning model. The regular instrumented and native builds
do not measure time per work package; macros remain only in instrumentation
implementation files and normal LTO can remove empty probe functions.

**These are observational, not controlled microbenchmarks.** A CPU-time clock query pair can cost as much as the operation it surrounds. Correlated operations
are not disentangled by timing only one of their jointly executed sites.
CPU clock granularity, sampling bias, compiler optimizations and machine
architecture limit interpretation. The micro timing code should be reviewed carefully before merge and
kept as a separately compiled diagnostic capability, not enabled in the
normal solver or work-based tuner.
Only change calibration coefficients with independently validated,
held-out improvements; don't rewrite the bundled model from these timings
alone.
