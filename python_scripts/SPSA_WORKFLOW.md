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
  --iterations 500 --lr 0.0001 --seed 42 --log scratch/tune.log
```

Without `--seed`, the tuner generates one and records it. Timing still depends on
the machine and system load. Each winner has an adjacent JSON sidecar containing
mode, seed, defaults, projected initial values, active parameters, optimizer
settings, revision, source/binary hashes, and hashes/counts of the loaded datasets.
Metadata starts as incomplete and is marked complete with the final winner.
The sensitivity report now averages absolute gradients, avoiding cancellation.

Post-tuning comparisons honor `--max-workers` and `--no-stdin`. By default they
run two rounds, baseline/optimized followed by optimized/baseline, with one
unmeasured warmup instance per worker per arm. This doubles measured comparison
work compared with the old single round. Adjust with `--comparison-repeats`
(a positive even number) and `--comparison-warmup`. Training iterations are unchanged.

For a standalone comparison:

```bash
python3 python_scripts/compare_performance.py --size 8 \
  --winners scratch/spsa_winners_s8_0.txt --max-workers 4 \
  --repeats 4 --warmup 1 --log scratch/comparison.log
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
Timeouts/errors and differing solution counts invalidate the comparison, withhold
the aggregate performance table and cause a nonzero CLI exit. They are never
silently omitted or replaced with artificial node counts. The current C stdin
protocol reports nodes but no solution count; its records therefore contain
`solutions: null`. Use subprocess mode or `verify_consistency.py` to check counts.

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
