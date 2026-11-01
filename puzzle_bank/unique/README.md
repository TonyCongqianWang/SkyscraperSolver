# Unique puzzle bank (schema v1)

The canonical bank is published as static JSON via GitHub Pages in the solver repository.

- `minimal/size_N.json`: verified unique, locally irreducible clue/given configurations.
- `candidates/size_N.json`: uniqueness-verified versions with extra visibility clues, **not yet difficulty-calibrated**.
- `matched/size_N.json`: curated, difficulty-matched puzzles intended for the game. Initially absent until calibration is implemented.

The game must use only `matched/` files. Avoid interpreting clue-count tiers as human difficulty.

Generate after `make`:

```bash
python3 python_scripts/puzzle_bank/generate_unique.py --size 5 --count 10 --attempts 200
```

A puzzle is accepted only when the native solver reports one solution using `-s 2`. Failed or timed-out checks are rejected. Cost is `visible_clue_count + 5 * given_cell_count` by default; reducing expensive given cells is prioritized. The generator uses shuffled cyclic Latin squares, not a uniform Latin-square distribution. The minimizer is deletion-based, so it produces an irreducible result, **not a proven globally minimum-cost puzzle**.

To publish JSON, enable **Settings → Pages → GitHub Actions** in this repository. The workflow deploys committed files from `puzzle_bank/unique/v1`. It does not generate puzzles in the deployment job. Example URL after publishing:

`https://tonycongqianwang.github.io/SkyscraperSolver/puzzle-bank/v1/minimal/size_5.json`

The repository's generated files should be reviewed before merging; later, a calibration job can populate `matched/` with explicit difficulty metadata.
