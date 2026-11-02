# Unique puzzle bank generator (v2)

The generator uses the existing randomized-backtracking seed + cycle-switch MCMC
sampler in `python_scripts/dataset_generation/generator.py`, rather than
shuffled cyclic Latin squares. MCMC has full-state sampling goals but is **not
claimed to be proven uniform**; `--burn-in` and `--gap` control sampling.

It writes a new **v2** format; existing `puzzle_bank/unique/v1/` files are
left unchanged. Building a full set of banks can be expensive since every
candidate is checked using the native solver with `-s 2`.

## Generate

```sh
make
python3 -m pip install -r python_scripts/dataset_generation/requirements.txt
python3 python_scripts/puzzle_bank/generate_unique.py --size 6 --count 100 \
  --attempts 1000 --burn-in 100000 --gap 100 --batch-size 64
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
asking for too many groups will fail without overwriting the output.

## Output

`puzzle_bank/unique/v2/minimal/size_N.json` and
`puzzle_bank/unique/v2/candidates/size_N.json` contain:

- `count`: canonical solution group count (the requested target).
- `puzzle_count`: total distinct minimal puzzles across those groups.
- `groups[]`: each group has an `id`, `canonical_solution` (flat row-major),
  and `puzzles[]`.
- Each minimal puzzle includes clues, givens, node count, and clue/given counts.
- Each candidate puzzle has a `variants[]` array with:
  - `minimal` (the original).
  - For each number of missing edge clues to add, up to four independently
    sampled subsets; there is only one complete-clues configuration.
  - For each number of additional given cells up to **one third of the grid
    filled in total**, up to four independently sampled subsets.
- Each variant has an individual `nodes_visited` measurement from a uniqueness
  check. All variants are guaranteed unique relative to the same completed grid
  at generation time. Variants are **not difficulty-calibrated**.
- `symmetry: D4_board_only` describes the frontend's future option to display
  any of eight orientations. The frontend must transform clues, givens, and
  completed grid consistently; the bank stores only the canonical orientation.

Candidate variants add either clues or givens to the minimal base, not both.
The cap on givens includes those already in the minimal puzzle. Identical
variants from symmetric sampling or exhausted combinations are not repeated.

The v2 format is intentionally different from v1; clients must explicitly
opt into it. Pages publishing of v2 JSON is separate from this generator change.

## Tests

```sh
python3 -m unittest python_scripts.tests.test_unique_puzzle_bank -v
```
