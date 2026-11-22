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

## One pooled regression fit, followed by measured unmerging

The calibration computes collinearity groups and runs **one pooled nonnegative
regression** on summed group counters. The grouped regression coefficients,
hyperparameters, and validation scores remain exactly as fitted. Afterward:

1. The first calibration phase has already collected native runtimes, all
   raw work counters, and sampled section CPU timings. For merged counter
   members, the section measurements provide initial relative-cost evidence.
2. A controlled benchmark runs **for every counter in the known merged
   groups**, independently of whether its section timings are available.
   Its repeated C operations include grid/setup checks, cache builds and
   copies, cache compaction checks/moves, line and transition
   comparisons/shifts, and index-copy overhead/volume. It uses the real
   solver structures, compiler optimizations, and independent timing rounds.
3. A log-ratio graph combines the measured evidence. Controlled measurements
   are weighted more heavily than the short, overhead-sensitive CPU section
   measurements; both contribute where available.
4. **No refit:** the merged regression coefficient is algebraically allocated
   to its members using the measured relative costs. The allocation is
   normalized to preserve the group's *total fitted contribution on training
   observations*. For exact collinearity it preserves each training
   prediction; for approximate collinearity, per-puzzle predictions can
   drift. The report quantifies this drift and evaluates the final allocated
   coefficients on held-out puzzles.
5. The compact `work_calibration.model.json` contains **the individually
   allocated coefficients** (not guessed equal weights), while keeping
   original merged coefficients, relative-cost evidence and allocation
   metadata. The separate collinearity JSON also includes these details.

If the benchmark cannot measure a member reliably, the workflow **fails
closed rather than inventing an equal-cost ratio or exporting a misleading
v3 model**. The controlled C harness must be extended if a new correlation
group contains operations it does not yet benchmark. This requirement is
intentional. Constant/unexcited counters remain excluded from fitting,
with explicit zero weights rather than invented independent costs.

### Run the complete calibration

```sh
python3 python_scripts/calibrate_work.py
```

The script creates:

- `scratch/work_calibration.raw.jsonl`: native, counter and section timing
  observations, written incrementally
- `scratch/work_calibration.json`: all four regression fits, group membership,
  micro timings, post-fit coefficient allocation, and held-out diagnostics
- `scratch/work_calibration.model.json`: **pooled allocated counter weights**
  for the tuning objectives
- `scratch/work_calibration.collinearity.json`: merged-group membership,
  timing-derived ratios, per-member coefficients, and evidence
- `scratch/work_calibration.micro.json`: controlled raw timings plus a
  further **independent** test of the allocated ratios on up to 32 fresh
  SPSA validation puzzles per size

The ordinary calibration automatically runs the controlled benchmark
**before export** and independent solver-section plausibility checks
after export. Use `--micro-repeats` and `--micro-rounds` to increase
measurement stability; at least three independent rounds are required.
`--no-micro-verify` skips only the *additional* validation-set check,
not the controlled benchmark needed to split merged coefficients.
`--no-section-timing` omits the sampled solver sections, but controlled
measurements still resolve merged groups.

For an inexpensive functional smoke run (the fitted model will not be
scientifically meaningful):

```sh
python3 python_scripts/calibrate_work.py --puzzles-per-size 4 \
  --native-repeats 3 --instrumented-repeats 2 --no-perturb \
  --no-micro-verify
```

The optional controlled/validation-set check can be repeated without
rerunning calibration:

```sh
python3 python_scripts/work_micro_probe.py \
  --model scratch/work_calibration.model.json \
  --collinearity scratch/work_calibration.collinearity.json \
  --output scratch/work_calibration.micro.json
```

### Interpreting timing evidence and plausibility

The detailed report contains `section_timing_plausibility` for training,
held-out puzzles, and each size. Its Pearson score measures the agreement
between measured and predicted time for the **same sampled operations**.
Coverage and the fraction of modeled work that was actually timed must be
considered alongside the correlation: a strong score on a narrow group of
operations does not validate the entire model.

The end-of-calibration independent check compares measured per-member
cost ratios with the deployed allocated coefficients. An agreement is
supporting plausibility evidence, not proof of universal hardware costs.
The controlled benchmark is a separate C executable with long timed
intervals, while section timing samples short real solver operations.
Their cost estimates can disagree due to caching, compiler effects,
input distributions and timing overhead; all evidence and differences
are retained. No regression is repeated or tuning coefficients silently
reoptimized after allocation.

**Important:** the newly added schema-v3 work features require a new
calibration. The bundled v2 model may still be used temporarily for
tuning through an explicitly limited compatibility projection, but it
does not include the added scan counters. The v3 model's real held-out
ranking performance is not known until the expensive run completes.
