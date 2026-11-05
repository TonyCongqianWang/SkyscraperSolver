# Solver for the Skyscraper puzzle game

Originally created for the Rush01 project during the C Piscine at 42 Heilbronn, this C solver now focuses on constraint propagation, search heuristics, and performance optimization.

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

For the original development notes, see [Version History](HISTORY.md).
