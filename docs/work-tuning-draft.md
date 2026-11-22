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
`python_scripts/tuning_objective.py`. Legacy tuning preserves previous
nodes/time mix and sweep weighting. In work mode, SPSA's two existing
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

## Experimental, optional micro timings

```sh
python3 python_scripts/work_micro_probe.py --puzzles-per-size 16
```

This builds `make INSTRUMENT=1 MICRO_TIMING=1` into a **separate**
`skyscraper_solver_work_micro` (never the tuning binary). Internal
begin/end probes sample every 64th cache-entry copy, line entropy scoring
and constraint-index copy, accumulating process CPU clock ticks. Output
`scratch/work_micro_probe.json` includes samples and provisional comparison
with pooled work coefficients. The regular instrumented and native builds
do not measure time per work package; macros remain only in instrumentation
implementation files and normal LTO can remove empty probe functions.

**These are observational, not controlled microbenchmarks.** A `clock()`
pair can cost as much as the operation it surrounds. Correlated operations
are not disentangled by timing only one of their jointly executed sites.
CPU clock granularity, sampling bias, compiler optimizations and machine
architecture limit interpretation. The micro timing code is meant to be
reviewed and removed before merge after collecting experimental evidence.
Only change calibration coefficients with independently validated,
held-out improvements; don't rewrite the bundled model from these timings
alone.
