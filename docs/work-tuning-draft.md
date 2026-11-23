# Draft: work-based tuning and measured time + nodes

The current work-counter schema contains 48 counters. The previously
bundled 33-counter model has been removed because it lacks the new
size-dependent work components. Run the full calibration and use its
`scratch/work_calibration.model.json` before work-based tuning. The only supported
work-counter schema is **v1**. The bundled model was trained using 14,976
observations and validated on 4,992 held-out observations.

Both **calibrated work** and **measured time + nodes** are first-class
tuning objectives. Calibrated work is the default, while the explicit
`--nodes-time` flag selects measured time and node counts for both SPSA
and sweep. Neither option is deprecated. The same numerical loss policy,
mode weighting and shifted-log references are centralized in
`python_scripts/tuning_objective.py`.

From a clean checkout:

```sh
./setup_and_tune.sh --size 8 --iterations 100
./setup_and_tune.sh --sweep --mode math8 --no-compare
./setup_and_tune.sh --size 8 --nodes-time --iterations 100
./setup_and_tune.sh --sweep --mode math8 --nodes-time
```

The wrapper builds a native solver for real comparisons and a dedicated
instrumented solver for work-based tuning. The work objective predicts
**seconds**, not clock time spent in the instrumented binary. Run metadata
includes the deployed model file and its SHA256.

## Calibration workflow

The default calibration now draws a *fresh random seed* and prints it.
A supplied `--seed N` deterministically reproduces puzzle sampling,
puzzle-level train/validation splits and simultaneous antithetic
SPSA-style perturbation pairs. The default has six such random
perturbation pairs per size (plus baseline) and 512 symmetry-distinct
puzzles of each size 7, 8 and 9. Source datasets are exclusively the
SPSA training files.

The fitter uses **milliseconds internally** for better numerical
convergence tolerance, but exports and predicts **seconds**. The fitted
merged groups are not refitted: sampled solver-section timing and
controlled microbenchmarks independently measure member costs, and
their ratios allocate the already-fitted pooled group coefficients.
Every member of a merged group must have reliable timing evidence;
equal-cost guesses are not accepted. The compact pooled model and
collinearity export record the final allocations and the original
group coefficients.

Run calibration with:

```sh
python3 python_scripts/calibrate_work.py
python3 python_scripts/calibrate_work.py --seed 123456
```

Outputs:

- `scratch/work_calibration.raw.jsonl`: native runs and instrumentation data
- `scratch/work_calibration.json`: detailed fitted and timed diagnostics
- `scratch/work_calibration.model.json`: compact pooled coefficients
- `scratch/work_calibration.collinearity.json`: merged-group splits and timing evidence
- `scratch/work_calibration.micro.json`: independent micro plausibility checks

The final timed-section validation checks up to 32 fresh SPSA validation
puzzles per size. `--no-micro-verify` skips this independent check, but
not the controlled microbenchmark required for the coefficient split.
`--no-section-timing` skips solver-section samples, leaving controlled
measurements as the sole timing source. If a newly observed merged group
does not yet have a benchmark, the calibration must fail rather than
manufacture an equal-cost ratio.

### Remaining validation work

The committed model was calibrated with size-7 enumeration and
size-8/9 first-solution runs. The pooled size-8 held-out clear-ranking
accuracy improved substantially, but size-8 enumeration and actual
SPSA batch objective ranking against native runtimes still require
validation. The PR remains a draft for that reason.
