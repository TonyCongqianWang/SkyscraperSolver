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
Training uses mean log((value + shift) / (reference + shift)) for each time/node term, preserving the existing mode weights and separate time/node gradient normalization, clipping and momentum. The shifted geometric means remain the comparison metrics. Final SPSA winners use SWA over at most the last 10 iterations. Training uses PAR-4 time charging (40 scored seconds for a 10-second timeout or subprocess failure) in both stdin and standalone modes, matching the default post-tuning comparison timeout policy; the legacy 100,000-node fallback remains for training failures.

The tuner defaults to four perturbation pairs per iteration; `--directions N`
controls this, and `--directions 1` retains the original single-pair sampling
and optimizer behavior. Each direction uses a portion of the configured batch,
with the same instances evaluated at its plus/minus perturbations. For a
power-of-two number of active parameters, Hadamard directions are exactly
orthogonal when the requested count does not exceed that number. Otherwise
independent randomized sign vectors are used. The requested direction count
must not exceed the batch size. Each iteration evaluates only the paired perturbations. The progress log reports gradient norms from those probes.

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
`--comparison-win-tolerance` to 0.10. Training still applies a 10-second per-instance runtime limit, but now scores timeouts at 40 seconds by default (PAR-4).

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

## Single-parameter sweeps

Use `--sweep` as the **first** wrapper argument to select the coordinate-sweep
script instead of SPSA:

```bash
./setup_and_tune.sh --sweep --mode math7 --seed 42 --no-compare
./setup_and_tune.sh --sweep --mode math8 --seed 42 --no-compare
./setup_and_tune.sh --sweep --mode math9 --seed 42 --no-compare
./setup_and_tune.sh --sweep --mode strategy --seed 42
./setup_and_tune.sh --sweep --mode effective-depth --seed 42
./setup_and_tune.sh --sweep --mode prune-line --seed 42
./setup_and_tune.sh --sweep --mode period-base --seed 42
```

`math7`, `math8` and `math9` each tune only the 22 size-specific math parameters (16 existing math parameters
plus six cache-period controls).
`math7` uses the mixed sizes-5–7 le7 dataset and tunes only `_LE7` parameters.
The le7 dataset is loaded only for `math7`; shared strategy sweeps
(including all the subsections below) evaluate sizes 8 and 9 exclusively.
`strategy` still tunes all 74 shared parameters. For shorter tuning sessions,
select a disjoint strategy subsection with `--mode`:

| Sweep mode | Parameters | Scope |
| --- | ---: | --- |
| `prune-global` | 5 | Global entropy pruning thresholds |
| `prune-grid` | 11 | Initial, constraint and lookahead grid-pruning thresholds |
| `prune-line` | 20 | Constraint and lookahead line thresholds, including their paired bounds |
| `lookahead-continue` | 10 | Lookahead continuation thresholds and slopes |
| `period-base` | 12 | Selection and depth-dependent period coefficients |
| `period-tiers` | 10 | Medium and heavy period multipliers |
| `effective-depth` | 6 | Effective-depth coefficients (existing subsection) |

The seven subsections are derived in `param_metadata.py`, alongside the existing
`effective-depth` group, and cover every strategy parameter exactly once. A subsection
sweep holds all other parameters at their current defaults; it does not
automatically inherit winners from another sweep. Apply desired winners before
starting a later session. Each mode writes its own uniquely named winner files.

The SPSA `--tune-mode strategy` also includes effective depth;
`--tune-mode effective-depth` selects it alone, and `--tune-mode math` selects
only size-specific math parameters.

Each invocation performs one pass in a seeded random parameter order, accepting
the best value before moving to the next parameter. The candidate grid is the
current value plus `0, ±0.5, ±1, ±2, ±4` normal SPSA perturbation widths, where a
width is `--perturb × perturb_scale × (max − min)` and `--perturb` defaults to
0.03. Candidate order is randomized. Bounds, integer rounding and pair constraints
can merge candidates; the script evaluates each distinct value once. Pair
constraints limit the selected coordinate's interval without moving another
parameter. Ties retain the current value.

The fixed, randomly subsampled training panels contain 2,048 le7 single-solution
instances and 512 le7 enumeration instances for `math7`, or 1,024 size-8
single-solution instances, 64 size-8 enumeration instances, and 2,084 size-9
single-solution instances. A math sweep loads only its own size. Each clue's
sampled symmetry is held fixed throughout the pass, and the sampled source
indices and transformed clues are recorded. `--s7-single`, `--s7-enumeration`,
`--s8-single`, `--s8-enumeration`
and `--s9-single` can override these counts; undersized banks fail explicitly.

The evaluator reuses SPSA's shifted-log losses and training timeout scoring.
The le7 objective uses `0.5 × single mean + 1.5 × enumeration mean` for each
loss (25% single / 75% enumeration, matching size 8), with a 70% time / 30% node
blend. Its shifts and reference scales remain the same as SPSA's le7 objective.
Size 8 retains `0.5 × single mean + 1.5 × enumeration mean` for each loss,
then combines `0.64 × time loss + 0.36 × node loss`. Size 9 combines
`0.66 × time loss + 0.34 × node loss`. Shared-parameter sweeps give the two
resulting size objectives equal weight. These fixed time/node weights approximate
recent SPSA gradient normalization. Cached current scores supply the no-move
candidate; only affected sizes are re-evaluated.

Unique sparse winners, progress logs and JSON provenance/checkpoints are written
under `scratch/sweep_winners_<mode>_<index>.*` by default. `--log` selects a progress
log path. The JSON includes the seed, parameter order, fixed panels, candidate
scores, selected values, source/binary hashes, and completion/comparison status.
Winners can be applied with `python_scripts/apply_winners.py`; sweeps do not
change defaults automatically.

Without `--no-compare`, the script invokes the same training-first-10% and full
validation comparisons as SPSA, for each applicable size. Math7 compares both
solution modes on le7 training and validation sets. Size 8 compares both
solution modes; size 9 compares single-solution mode. Shared sweeps use separate
`_s8` and `_s9` comparison filenames. Comparison repeats, warmup, timeout and
penalty flags match SPSA. The final winner is saved before comparison, so a
comparison failure does not discard completed tuning.


## Independent selection-cache periods

Each size group (`LE7`, `S8`, `S9`) has an overall `SEL_PERIOD_SCALE_*` and
five operation-specific factors:

- `SEL_CACHE_COMPACT_PERIOD_*`: remove filled/invalid cached transitions.
- `SEL_CACHE_RESCORE_PERIOD_*`: refresh the base branch-selection scores.
- `SEL_CACHE_BLEND_PERIOD_*`: age the blended lookahead scores.
- `SEL_CACHE_SORT_PERIOD_*`: reorder cached transitions by their stored scores.
- `SEL_CACHE_LINE_SORT_PERIOD_*`: refresh the constraint-line order.

These factors default to 1, have bounds 0–16, and belong to the corresponding
math tuning group, including math7. A larger factor allows more reuse. The
existing shared `SEL_PERIOD_COEF_SQRT` and `SEL_PERIOD_COEF_INV` determine the
progress-dependent base period. Each operation uses that period multiplied by
its size's overall scale and its own factor (integer entropy units). Each has
its own last-refresh entropy stamp. Zero is eager maintenance on each eligible
cache access. Initial cache construction still populates all scores/orders.

Completing a main-level two-sided lookahead pass marks blended scores dirty.
The next cache access consumes those scores even if periodic maintenance is
suppressed; it does not force compaction, base rescoring, transition sorting, or
line sorting. Base-score refresh likewise dirties the blend. The blend period
controls subsequent score aging, not whether newly recorded results are consumed.
Sorting retains an independent schedule even after score updates.
At a scheduled sort, unchanged scores and the same selection criterion reuse
the current order. The refresh stamp still advances, preserving the schedule.

Within a branch domains shrink, so initial candidate collection is sufficient:
subsequent compaction removes candidates without scanning for new ones or
reconciling old metadata. Cache mutations use copy-on-write with matching
line-order frames, preserving parent cache state across children and probes.
Cache state is bundled separately from candidate storage: cloning assigns the
state struct and copies only the retained candidate/metadata prefix. Cloning
does not compact that prefix; inactive array capacity is left untouched.
A reused order still checks each candidate's current validity before selecting it.
