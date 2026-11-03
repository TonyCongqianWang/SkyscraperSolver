# Puzzle bank generation

The current datasets are `puzzle_bank/unique/v1/minimal/size_N.json` and
`puzzle_bank/curated/v1/size_N.json` for sizes 4–9.

The generator samples Latin squares using MCMC, groups canonical solutions
modulo board D4 symmetries, and verifies each minimal configuration with the
native solver (`-s 2`). Minimized means locally irreducible, not globally
minimum cost. The sampling is not proven uniform.

Run `make`, install `python_scripts/dataset_generation/requirements.txt`, then
execute `bash generate_unique_banks.sh`. The wrapper generates minimal banks
and calls `fill_curated.py` to add mixed clue/given candidates directly from
the minimal banks. Curated quotas are in
`puzzle_bank/curated/v1/quotas.json`. The filler retains existing puzzles,
regrades them, and stops when quotas are satisfied or its configured stall
limit is reached. No quotas are guaranteed achievable.

Difficulty levels, ordered from easiest to hardest:

`very_easy`, `easy`, `medium`, `hard`, `very_hard`,
`extreme`, `extreme_plus`, `extreme_plus_plus`.

The levels are heuristic solver-search thresholds, not human-tested ratings.
`curate.py` contains the shared grading policy, and
`fill_curated.py` is the primary curation path.

The GitHub Pages builder `web/build_site.py` validates the hydrated banks,
publishes curated records sharded by size and difficulty under
`/assets/puzzles/curated/v1/`, and computes percentiles and histograms for
solver nodes, main nodes, visibility clues and given cells. Published JSON is
not required to match repository file layout. Historical internal version
labels in existing LFS payloads are normalized to public v1 by the exporter.

Tests: `python3 -m unittest discover -s python_scripts/tests`.
