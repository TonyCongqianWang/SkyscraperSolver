# Unique puzzle bank generator (v2)

The generator uses the existing randomized-backtracking seed + cycle-switch MCMC
sampler in `python_scripts/dataset_generation/generator.py`, rather than
shuffled cyclic Latin squares. MCMC has full-state sampling goals but is **not
claimed to be proven uniform**; `--burn-in` and `--gap` control sampling.

The puzzle-bank generator imports `MCMCLatinSquareSampler` from the existing
`dataset_generation/generator.py` module. The sampler fills a buffer of
10,000 squares using 250 samples from each freshly seeded MCMC chain (40
segments per buffer). Each chain receives its own burn-in; the completed
buffer is shuffled before individual squares are consumed. Sampling does
not depend on whether the downstream puzzle generator accepts a group.
Set `--batch-size` and `--reseed-interval` to override these defaults.

It writes a new **v2** format; existing `puzzle_bank/unique/v1/` files are
left unchanged. Building a full set of banks can be expensive since every
candidate is checked using the native solver with `-s 2`.

## Generate

```sh
make
python3 -m pip install -r python_scripts/dataset_generation/requirements.txt
python3 python_scripts/puzzle_bank/generate_unique.py --size 6 --count 100 \
  --attempts 1000 --burn-in 100000 --gap 100 --batch-size 10000 --reseed-interval 250
```

`--count` counts **distinct completed solutions modulo the eight D4 board
symmetries** (rotations and reflections). Heights are **not** relabeled:
changing height labels can change visibility. Repeated samples of a canonical
solution may yield additional distinct minimized clue/given configurations;
these are stored under the same group. Duplicates of the same configuration
within a group are suppressed.

Sampling stops once the requested number of solution groups is obtained.
`--attempts` caps sampled solutions, including those rejected or repeated.
For small sizes, the number of available canonical solutions is finite, so
requests above the known Latin-square total are capped. Size 4 uses the exact
74 distinct D4-orbit limit; for sizes 5–9 the total number of Latin
squares is only a conservative upper bound, not an exact D4-orbit count.
A smaller unattainable request can still exhaust `--attempts` without output.

Alternatively, run `bash generate_unique_banks.sh` from the repository root.\nIt generates only minimal puzzles for sizes 4–9 in `puzzle_bank/unique/v3/minimal`\n(1000 target groups, capped at 74 for size 4; 100000 attempts each), then\nuses those minimal puzzles to fill `puzzle_bank/curated/v2` with mixed\nclue/given candidates, using `puzzle_bank/curated/v2/quotas.json`.\nAdditional wrapper arguments are passed to minimal puzzle generation only.

## Output

`puzzle_bank/unique/v2/minimal/size_N.json` and
`puzzle_bank/unique/v2/candidates/size_N.json` contain:

- `count`: canonical solution group count (the requested target).
- `puzzle_count`: total distinct minimal puzzles across those groups.
- `groups[]`: each group has an `id`, `canonical_solution` (flat row-major),
  and `puzzles[]`.
- Each minimal puzzle includes clues, givens, total `nodes_visited`,
  `main_nodes_visited`, and clue/given counts.
- Each candidate puzzle has a `variants[]` array with:
  - `minimal` (the original).
  - For each number of missing edge clues to add, up to four independently
    sampled subsets; there is only one complete-clues configuration.
  - For each number of additional given cells up to **one third of the grid
    filled in total**, up to four independently sampled subsets.
- Each variant has both `nodes_visited` and `main_nodes_visited` measurements from a uniqueness
  check. All variants are guaranteed unique relative to the same completed grid
  at generation time. Variants are **not difficulty-calibrated**.
- `symmetry: D4_board_only` describes the frontend's future option to display
  any of eight orientations. The frontend must transform clues, givens, and
  completed grid consistently; the bank stores only the canonical orientation.

The greedy minimizer preferentially attempts removal of smaller given heights
and edge clues farther from visibility 3. Within the original cost tiers,
removal order is drawn without replacement using weights proportional to
`exp(-0.25 * height)` for givens and `exp(0.25 * abs(clue - 3))` for edge clues.

Candidate variants add either clues or givens to the minimal base, not both.
The cap on givens includes those already in the minimal puzzle. Identical
variants from symmetric sampling or exhausted combinations are not repeated.

The v2 format is intentionally different from v1; clients must explicitly
opt into it. Pages publishing of v2 JSON is separate from this generator change.

## Tests

```sh
python3 -m unittest python_scripts.tests.test_unique_puzzle_bank -v
```

## Offline distribution statistics

Run `python3 python_scripts/puzzle_bank/analyze_candidates.py` from the repository root to aggregate v2 candidates for sizes 4–7 into `candidate_stats.json` without exporting solution grids. Use `--directory`, `--sizes`, and `--output` to target a curated bank or different versions. The report includes minimum and maximum alongside quantiles for total and main nodes, histogram bins, and clue/given breakdowns. This compact report can be used as an input when generating static curated index statistics; do not publish the full candidate files.

## Curating candidates

The raw v2 candidate sets may remain in Git LFS or release artifacts; they are
not needed by GitHub Pages. Run this offline after generation:

```sh
python3 python_scripts/puzzle_bank/curate.py --sizes 4 5 6 7 8 9 \
  --source puzzle_bank/unique/v2/candidates \
  --output puzzle_bank/curated/v1 --max-per-band 15000
```

The curated namespace has **independent versioning**. For each size, the
script saves up to 15,000 variants per difficulty using deterministic uniform
reservoir sampling; the source count and selected count are both recorded.
Every curated variant stores its parent `minimal_puzzle_id`, canonical
`solution_group_id`, variant label, clues, givens, total nodes and main nodes.
The per-size files and compact `statistics.json` are intended for publishing
without exposing candidate files.

Difficulty rules (main-node overrides dominate):

| Main nodes | Total nodes | Band |
|---|---|---|
| 1 | <=50 / <=100 / <=200 / <=400 | very_easy / easy / medium / hard |
| 1 | >400 | very_hard (capped) |
| 2 | <=400 / >400 | hard / very_hard |
| 3–8 | <=400 / <=800 / <=1600 / >1600 | hard / very_hard / extreme / extreme_plus |
| >8 | any | impossible |

The supplied thresholds have gaps or conflicts for some node/main-node pairs;
these explicit floor/cap rules ensure every candidate gets exactly one band.
They are provisional difficulty heuristics, not validated human difficulty.
The curator is independent of the generator: a future v3 generator can use
a Cartesian product of extra clues and givens, with eight randomly selected
candidate configurations per minimal puzzle rather than exhaustively enumerating
the grid.

## Directly filling curated quotas (without candidate files)

Intermediate `puzzle_bank/unique/v2/candidates/` JSON is ignored and removed
from this branch; only the minimal and curated datasets need to be retained.
The LFS attribute is restricted to generated minimal banks, not curated JSON.
Pull the minimal LFS objects locally before running the filler.

Edit `puzzle_bank/curated/v2/quotas.json`: each size and difficulty has a
nonnegative minimum. The defaults are 10,000 except very_easy for all sizes
and hard through impossible for size 4, which have zero minimum. The filler
continues collecting candidates for all buckets (up to 15,000 each) while
any minimum is unmet; a met minimum does not stop that bucket from growing.
All-zero minima generate no solver work; existing curated entries are preserved. To generate new mixed
clue/given candidates directly from the minimal bank, run:

```sh
python3 python_scripts/puzzle_bank/fill_curated.py --sizes 4 5 6 7 8 9
```

The script randomly samples **Cartesian products** of extra edge-clue and
prefilled-cell density levels and random subsets at each density. It verifies
uniqueness with the native `-s 2` solver, calculates both node metrics, and
appends qualifying variants until all minima are reached or the configured
per-minimal sampling limit is exhausted. `max_attempts_per_minimal` defaults to
100 in the JSON config. Running it repeatedly preserves selected entries;
there is no guarantee all quotas are reachable. The output retains the
minimal puzzle and canonical solution group IDs.

The original candidate-based curator (`curate.py`) is still available for
any local historical candidate files, but candidate storage isn't required.
