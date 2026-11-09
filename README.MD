# Solver for the Skyscraper puzzle game

Originally created for the Rush01 project during the C Piscine at 42 Heilbronn, this C solver now focuses on constraint propagation, search heuristics, and performance optimization.

## Release v1.0.0

This release follows v09 and introduces the `vMAJOR.MINOR.PATCH` naming format.
It brings a redesigned search and lookahead engine, broader test-driven
verification, versioned puzzle curation, and a static website with a browser
solver and puzzle API. See the [release highlights](HISTORY.md#v100) for details.

The published website builds its WebAssembly solver from the latest published
GitHub release, while CI continues to build and test current development code.
Website publishing runs on website or published puzzle-data changes and new
stable releases; it can also be started manually.

## Play online

- [Play the Skyscrapers web game](https://tonycongqianwang.github.io/SkyscraperGameWeb/)
- [Try the C solver in your browser](https://tonycongqianwang.github.io/SkyscraperSolver/demo/) (WebAssembly)
- [Explore curated puzzles](https://tonycongqianwang.github.io/SkyscraperSolver/curated/)

An earlier [C#/.NET version](https://github.com/TonyCongqianWang/SkyscraperGame) is also available.

## Compilation and usage

Build with `make`:

```sh
make
```

Or compile directly:

```sh
cc -Wall -Wextra -Werror -O2 -o skyscraper_solver src/*.c
```

Lookahead probe depths are defined per pruning tier (light, medium, heavy) in
`src/lookahead_depth.c`, using the extern array declared in `lookahead_depth.h`.
All three default to depth 1; initial pruning uses the heavy tier.

CI tests depths `{3, 2, 1}` for light, medium, and heavy tiers by replacing that
definition before building the normal solver.
To reproduce in a separate checkout:

```sh
cp python_scripts/tests/config/lookahead_depth_ci.c src/lookahead_depth.c
make re
for dataset in benchmark_sets/benchmarkSet7_python20.txt \
               benchmark_sets/benchmarkSet8_python20.txt \
               benchmark_sets/benchmarkSet9_minimal20.txt; do
  counts="benchmark_sets/_num_solutions_$(basename "$dataset")"
  make test VERIFY_ARGS="$dataset --expected $counts"
done
```

CI verifies all 20 puzzles in each Python solver dataset, including exhaustive and
finite-limit counts. Omit `VERIFY_ARGS` to run the default verification suite.

Probe depth bounds the search beneath each hypothesis; it is separate from
`MAX_LOOKAHEAD_DEPTH`, which limits nested lookahead contexts.

Run the solver with a space-separated list of clues:

```sh
./skyscraper_solver "5 2 3 2 2 1 4 1 3 3 3 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 3"
```

Grids up to 9×9 are supported. Clues are ordered top (left to right), bottom (left to right), left (top to bottom), and right (top to bottom). Use `0` for an unspecified clue. An optional second space-separated argument supplies pre-filled grid values, with `0` for empty cells.

The optional `-s <n_solutions>` flag controls solution enumeration. By default, the solver stops after the first solution. A positive value searches for up to that many solutions. `-s 0` enumerates and counts **all** solutions, retaining the most recently found solution grid and displaying that one grid in the normal CLI. The argument must be a nonnegative decimal integer within the supported unsigned 64-bit range.

## Python cross-checking solver

[python_solver/](python_solver/) provides an independent reference solver using Z3 or OR-Tools CP-SAT to cross-check solution counts and cell assignments.

```sh
pip install -r python_solver/requirements.txt
```

## Auxiliary tools and benchmarking

[python_scripts/](python_scripts/) contains tools for puzzle generation, benchmarking, verification, and parameter tuning (including SPSA). [benchmark_sets/](benchmark_sets/) and [puzzle_bank/](puzzle_bank/) hold test and evaluation instances. These tools are not required to build or run the C solver.

For release highlights and earlier development notes, see [Version History](HISTORY.md).
