---
name: spsa_analysis_and_winners
description: Analyze SPSA winner files and run provenance, interpret tuning and validation reports, and prepare or apply selected parameter updates to the solver and tuning defaults.
---

# SPSA tuning, analysis and winners

Run commands from the repository root. Keep downloads, proposed winners, analysis
scripts and reports under `scratch/`. Read [SPSA_WORKFLOW.md](../../../python_scripts/SPSA_WORKFLOW.md)
for detailed CLI options and SGM shifts; follow [repository rules](../../AGENTS.md)
for phase boundaries and verification. For remote artifacts, use the
[Kaggle run skill](../kaggle_kernel_runs/SKILL.md).

## Establish the sample and baseline

- Distinguish notebook versions, completed tuning runs, checkpoints and winner
  files. A notebook that errors or reaches Kaggle's execution limit during
  comparison can still have a valid final tuning winner. Use the winner JSON's
  `complete` flag and final/checkpoint label; do not filter final winners solely
  by validation success. Report missing or incomplete runs separately.
- Winner text files are intentionally sparse: only parameters actually tuned for
  that mode/size are written. Active parameters with zero final movement remain
  included; frozen parameters are excluded. Never fill absent entries with zero
  or treat unrelated historical defaults as tuned observations.
- Use `active_parameters`, `tune_mode` and size from provenance. For historical
  full files, exclude other sizes and inactive parameters. Relevant math names
  end in `_LE7`, `_S8`, or `_S9`; strategy names can be shared across sizes.
- Prefer recorded `initial_parameters` (projected physical starts), then recorded
  defaults. The analyzer can parse an archived `param_metadata.py` without
  executing it. Current defaults are an explicitly unverified fallback, not
  historical evidence. Local files without sidecars need an explicit baseline
  assumption; preserve them and report results with/without them when useful.
- Retain seeds, dataset identities, source revisions/hashes, direction counts,
  iterations, batch sizes and worker settings. Detect repeated copies/checkpoints
  of one run; do not count them as independent seeds. Equal rounded values alone
  do not establish that independently seeded runs are duplicates.

## Analyze directional evidence

```bash
python3 python_scripts/analyze_spsa_runs.py 'scratch/kaggle/v*/spsa_winners*.txt' \
  --alpha 0.05 --json scratch/analysis.json
# Add --size 8 or --size 9 when that restriction is part of the requested analysis.
```

The analyzer keeps strict size/mode/provenance/optimizer cohorts, including
`directions`. Its statistical helpers are in `python_scripts/spsa_statistics.py`.

- Use an **exact two-sided binomial sign test** against a 50/50 up/down null.
  Exclude numerical ties from the trial count and report up/down/tie counts and
  the actual per-parameter sample size. Use two sides when direction is chosen
  after inspecting the data.
- Use **Holm correction** at declared family-wise alpha (default 0.05). Correct
  all examined parameter/cohort tests together, not only promising rows or
  separately selected directions. The CLI reports raw `P SIGN`, adjusted
  `P HOLM` and the supported direction. There is no fixed 80% agreement rule.
- When the user requests a synthesis across script revisions, verify common
  starts and relevant data/settings first. Show subgroup directions and medians
  (e.g. one versus four directions, run lengths, machines). Pool compatible
  directional evidence explicitly; do not silently disable cohort safeguards.
  For a custom pooled table, call `binomial_sign_test(up, down)` for each row,
  then `adjust_direction_tests(all_parameter_rows, alpha)` across the whole
  declared family. Its hypothesis family differs from the strict CLI's family.
- Report median physical values and displacement alongside significance. The
  legacy `S_ratio = abs(median - start) / population_std` and its spread labels
  are descriptive heuristics, not significance tests or selection thresholds.
- Sign tests assume independent runs and a defensible fair-sign null. Shared
  data, optimizer/projection bias and subgroup disagreements matter. A small
  p-value establishes repeatable drift under that model, not runtime benefit or
  an optimum. Do not interpret a p-value as the probability a change is good.

A useful result includes sample/provenance coverage, proposed medians, directional
counts and adjusted p-values, subgroup checks, weaker/contradictory trends, and
an apply-ready file containing only the selected changes. Validation evidence
concerns whole winner vectors; it does not isolate each parameter's effect.

## Interpret current tuning and comparison output

- `spsa_tune.py` defaults to four perturbation directions, partitioning the batch
  budget between them. `--directions 1` retains the single-direction mode. Record
  `--seed`; missing seeds are generated and saved in the winner sidecar.
- Final values normally use SWA. The final table shows projected start, final
  physical value and absolute change. Sensitivity is average absolute combined
  raw gradient before clipping/momentum; it is unavailable for one direction,
  although absolute parameter changes are still shown.
- `GradNormClipped(T/N)` is the L2 norm across parameter components, after clipping
  and before EMA division. `GradEMA(T/N)` is its running scale;
  `GradNormalized(T/N)` is the norm entering momentum. Time and node gradients
  have separate EMAs. A large clipped norm alone does not imply a large step.
- Comparisons default to two balanced AB/BA rounds, fixed worker settings and
  one unmeasured warmup per worker/arm. Current comparison timeout is **10 s**;
  **PAR-4** assigns each timeout **40 s** in timing summaries. These are configurable
  with standalone `--timeout`/`--timeout-penalty` or tuning
  `--comparison-timeout`/`--comparison-timeout-penalty`.
- Timeouts remain in timing metrics and do not invalidate comparisons. Solver
  errors, missing/misaligned results and known solution-count mismatches do.
  Node metrics use only pairs completed by both arms, with sample counts; never
  invent a final node count for a timeout. All-timeout sets have valid penalized
  timing statistics but unavailable node statistics.
- Report solved/timeouts/errors, decisive wins and within-10%-of-fastest wins.
  A solve beats a timeout; both-timeout cases get neither a win nor a timing tie.
  Two successful times within the configurable 10% tolerance are ties and both
  receive a near-best win. Counts are per-round medians/ranges, not additional
  independent puzzles. Preserve JSONL measurements and JSON per-instance outcomes.
- Legacy timeout-excluding/invalid reports and different timeout penalties must
  be labeled separately. The stdin protocol lacks solution counts; null counts
  are not correctness verification. Use subprocess mode or consistency tests
  when solution-count checks are needed.

## Apply selected changes when authorized

Use a sparse `#define NAME VALUE` or `NAME = VALUE` file, not a full historical
winner dump. Respect the user's current scope and standing authorization; an
analysis task does not itself launch a new SPSA sweep or benchmark experiment.

```bash
python3 python_scripts/apply_winners.py scratch/selected_winners.txt
norminette src/
make re
micromamba run -n solver make test
micromamba run -n solver bash setup_and_tune.sh
```

The apply script updates mapped C parameters and `python_scripts/param_metadata.py`
by default. Inspect the diff for only selected entries and effective formatting
precision. Require **zero Norminette errors** and report notices separately.
`setup_and_tune.sh` without arguments verifies baseline/override setup without
launching tuning. If mamba's cache lock is inaccessible, a workspace-local
`XDG_CACHE_HOME="$PWD/scratch/mamba_cache"` can be used. Report verification and
any limitations before starting broader experiments.

Dataset construction is a separate workflow: see
[dataset_generation/README.md](../../../python_scripts/dataset_generation/README.md)
and the current `generate_spsa_datasets.sh` options rather than assuming an old
mix, size selection or generation timeout.
