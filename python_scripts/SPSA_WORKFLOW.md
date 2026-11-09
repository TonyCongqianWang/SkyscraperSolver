# SPSA runs and comparisons

The tuner and comparison script share `spsa_metrics.py`. Training shifts remain:

| Size | Mode | Time shift (seconds) | Node shift |
|---|---|---:|---:|
| 7 | Single | 0.002 | 100 |
| 7 | Enumeration | 0.005 | 1,000 |
| 8 | Single | 0.2 | 10,000 |
| 8 | Enumeration | 2.0 | 100,000 |
| 9 | Both | 1.0 | 120,000 |

For a reproducible sampling and perturbation sequence, pass `--seed`:

```bash
python3 python_scripts/spsa_tune.py --size 8 --tune-mode math \
  --iterations 500 --lr 0.0001 --seed 42 --directions 4 --log scratch/tune.log
```

Without `--seed`, the tuner generates one and records it. Timing still depends on
the machine and system load. Each winner has an adjacent JSON sidecar containing
mode, seed, defaults, projected initial values, active parameters, optimizer
settings, revision, source/binary hashes, and hashes/counts of the loaded datasets.
Metadata starts as incomplete and is marked complete with the final winner.
Winner text files (including intermediate checkpoints) contain only parameters
actually tuned for the selected mode and size; frozen parameters are excluded.
Active parameters whose final value happens to equal their start value are still
included. The JSON sidecar retains full defaults and initial values for provenance.
The final console/log table shows each tuned parameter's projected starting value,
final SWA value and absolute change in physical units (rounded for integer settings).
The sensitivity table also reports that absolute change and includes only tuned
parameters.
The tuner defaults to four perturbation pairs per iteration; `--directions N`
controls this, and `--directions 1` retains the original single-pair sampling
and optimizer behavior. Each direction uses a portion of the configured batch,
with the same instances evaluated at its plus/minus perturbations. For a
power-of-two number of active parameters, Hadamard directions are exactly
orthogonal when the requested count does not exceed that number. Otherwise
independent randomized sign vectors are used. The requested direction count
must not exceed the batch size. Full-batch monitoring remains unchanged.

For two or more directions, sensitivity reports the average across iterations
of the absolute *combined* raw gradient (after directional averaging, before
clipping and momentum). One direction reports N/A for sensitivity, while still showing absolute parameter
changes; a single SPSA pair cannot distinguish per-parameter absolute sensitivity.

Post-tuning comparisons honor `--max-workers` and `--no-stdin`. By default they
run two rounds, baseline/optimized followed by optimized/baseline, with one
unmeasured warmup instance per worker per arm. This doubles measured comparison
work compared with the old single round. Adjust with `--comparison-repeats`
(a positive even number) and `--comparison-warmup`. The per-instance comparison
limit defaults to **10 seconds**, configurable with `--comparison-timeout`.
`--comparison-timeout-penalty` defaults to 4 and
`--comparison-win-tolerance` to 0.10. Training iteration timeouts are unchanged.

For a standalone comparison:

```bash
python3 python_scripts/compare_performance.py --size 8 \
  --winners scratch/spsa_winners_s8_0.txt --max-workers 4 \
  --repeats 4 --warmup 1 --timeout 10 --timeout-penalty 4 \
  --win-tolerance 0.10 --log scratch/comparison.log
```

The standalone baseline uses `--baseline`; post-tuning comparisons use the same
tunable binary with default versus tuned environments. Baseline environments
exclude inherited parameter overrides. Use the same binary without overrides for
an A/A control. `--no-use-stdin` selects the subprocess-per-instance mode.

Each comparison writes per-instance JSONL and a JSON summary alongside its log
(or to `scratch/` if no log is supplied). `--records` selects the standalone JSONL
path. Records include dataset label, input index/clue, round, evaluation order,
arm, time, nodes, status and solution count when available. Summary tables show
median per-round metrics, median paired percentage changes and their ranges.
Timeouts are normal benchmark outcomes and do not invalidate a comparison.
Timing summaries include every instance, assigning each timeout `penalty × limit`
seconds: by default **40 seconds (PAR-4)**. Raw elapsed time and status are preserved
alongside `scored_seconds`, timeout and penalty in JSONL. The timing shift is
applied after charging timeouts. Errors, missing/misaligned records and differing
known solution counts still invalidate the comparison and cause a nonzero exit.
A successful-versus-timeout pair cannot be checked for matching solution counts.

Node summaries use only pairs completed by both solvers within each round; their
sample counts are printed. A timeout has no trustworthy final node count, so no
node penalty is invented. If no pairs finish, node metrics are `n/a` while the
penalized timing summary remains valid. Both-timeout instances stay in the timing
summary at the same penalty for both solvers and receive no win.

The outcome table shows solved instances, timeouts, errors, decisive wins and
near-best wins. A successful solve beats a timeout. With both solved, runtimes
within 10% of the faster time are ties; otherwise the faster solver wins.
Near-best wins count every solver within 10% of the fastest successful solve,
so both solvers can receive one on a tied instance. `--win-tolerance` changes the
relative tolerance. Every round persists its per-instance outcome in the JSON
summary. Counts are per-round medians with min/max ranges, never pooled as
additional independent puzzles.

This follows SCIP's separation of solved/timeout/error counts and its
[within-10%-of-fastest wins convention](https://www.scipopt.org/scip/doc/html/TEST.php).
Unlike SCIP's optimization-specific handling of unfinished primal bounds, our
both-timeout pairs are unranked because the puzzle protocol supplies no comparable
progress bound. Gurobi publishes
[penalized geometric runtime means (PAR-10)](https://www.gurobi.com/misc/lp/all/unmatched-performance);
our PAR-4 multiplier is an explicit policy choice, not a universal benchmark
standard. Balanced repeated comparisons retain timing variability, consistent
with [Gurobi's comparison guidance](https://support.gurobi.com/hc/en-us/articles/26992650628369-How-can-I-make-accurate-comparisons).

The current C stdin protocol reports nodes but no solution count; its records
therefore contain `solutions: null`. Use subprocess mode or
`verify_consistency.py` to check counts.

Fetch winners with the existing `fetch_kaggle_runs.py` commands. Adjacent JSON
metadata is downloaded automatically, and multiple winners in a version receive
distinct names even with an index-only destination template. Transient network,
rate-limit and server errors are retried with bounded backoff; downloads replace
the destination only after success.

```bash
python3 python_scripts/analyze_spsa_runs.py --size 8 'scratch/run_s8_*.txt' \
  --json scratch/analysis.json
python3 -m unittest discover -s python_scripts/tests -v
```

Analysis uses recorded initial values and groups by size, mode, defaults,
datasets, sources and optimizer settings; seeds may differ within a cohort.
Legacy downloads can use a sibling historical `param_metadata.py` snapshot
(parsed without executing it), plus the fetch manifest for mode. Otherwise the
analyzer explicitly labels its current-defaults fallback as unverified.

Every parameter reports its own sample count and up/down/tied counts. The signal
to spread thresholds are exactly 2 for strong and 1 for moderate, with no extra
percentage-shift threshold. A single sample is insufficient. This ratio measures
parameter displacement, not statistical significance or measured performance.

Directional evidence uses an exact two-sided binomial sign test against a 50/50
up/down null, excluding numerical ties from its sample size. The direction is
not assumed in advance. The analyzer reports raw `P SIGN`, Holm-adjusted
`P HOLM`, and a supported direction at family-wise alpha 0.05 (`--alpha` changes
this). The correction family includes **all parameter/cohort tests displayed by
that invocation**, not just promising parameters. Different direction counts are
also part of cohort identity. A fixed agreement percentage is not a selection rule.

The exploratory `TUNE DIR` column flags candidates at raw `P SIGN` ≤ 0.05.
Six unanimous non-tied runs pass this screen in either direction (p = 0.03125).
Five unanimous runs fall short (p = 0.0625). Use this column to shortlist
parameter changes for validation. Screening many parameters can produce false
positives, so `HOLM DIR` separately reports family-wise evidence.

Holm accommodates dependence between parameter tests, but sign-test calibration
still assumes independent runs with fair signs under the null. This tests update
direction repeatability conditional on the data/optimizer, not runtime benefit;
projection or optimizer bias can also cause directional drift. Keep effect sizes,
provenance and optimizer-family comparisons alongside the p-values. The existing
signal-to-spread labels remain descriptive heuristics, not significance decisions.

Method references: [exact binomial test](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/binom.test.html)
and [Holm adjustment](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html).
