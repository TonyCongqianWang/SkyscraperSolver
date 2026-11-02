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

Alternatively, from the repository root run `bash generate_unique_banks.sh` to
generate sizes 4–9 with 1000 target solution groups (capped at 74 for size 4)
and 100000 attempts per size. Additional arguments to the wrapper are passed
to each generator invocation.

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
