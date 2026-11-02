# Solver for the Skyscraper puzzle game

Originally created for the Rush01 project during the C Piscine at 42 Heilbronn. Since then, the solver has grown into a larger project focused on constraint propagation, search heuristics, and performance optimization.

> [!NOTE]
> This repository was originally a subdirectory within the [42HeilbronnCPiscine](https://github.com/TonyCongqianWang/42HeilbronnCPiscine) repository. It has been extracted into this standalone repository to facilitate easier tracking, independent usage, and clean integration.

## Play online — no installation required

**[Play my Skyscrapers web game](https://tonycongqianwang.github.io/SkyscraperGameWeb/)** — an interactive version with visible candidate domains and assistance while you solve.

**[Try the C solver in your browser](https://tonycongqianwang.github.io/SkyscraperSolver/solver/)** — enter visibility clues and an optional starting grid, click **Solve!**, and see the first solution and whether the puzzle is unique. The solver runs locally through WebAssembly: **no download, compilation, or installation needed.**

The [SkyscraperSolver GitHub Pages homepage](https://tonycongqianwang.github.io/SkyscraperSolver/) also links to the static puzzle-bank API for applications.

Other worthwhile Skyscrapers implementations include [Simon Tatham's Towers](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/towers.html) and [Puzzle Baron's Skyscrapers](https://skyscrapers.puzzlebaron.com/). For a separate offline C#/.NET GUI implementation, see my earlier [SkyscraperGame](https://github.com/TonyCongqianWang/SkyscraperGame) project.


## Compilation and Usage

Build with `make`, or compile directly (assuming `cc` is your C compiler):

```
make
```

For direct compilation:

```
cc -Wall -Wextra -Werror -O2 -o skyscraper_solver src/*.c
./skyscraper_solver "3 0 0 0 2 4 1 5 2 4 3 0 4 3 0 0 4 0 2 2 0 3 4 3 0 0 0 3 0 0 0 2" "0 0 0 0 0 0 0 1 0 0 8 0 0 2 0 0 0 0 0 5 0 0 0 0 0 0 0 1 0 0 0 0 0 0 5 3 0 0 0 0 0 0 0 2 0 0 1 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0 0 0"
./skyscraper_solver "2 3 2 4 3 2 1 5 1 3 2 3 2 4 5 4 2 3 3 2 5 3 3 1 2 4 3 2 1 2 2 5" "0 3 0 0 5 0 0 0 1 0 0 5 0 0 0 0 3 0 6 0 2 0 0 0 0 0 0 1 0 0 6 0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0 1 4 0 0 0 0 0 1 0 0"
```

On Windows:

```
.\skyscraper_solver "5 3 2 1 3 4 1 2 4 2 2 3 4 3 2 3 2 1 3 4 2 1 2 3"
```

Grids up to size 9x9 are supported. Constraint values (clues) must be given in this order: top (left to right), bottom (left to right), left (top to bottom), and right (top to bottom), with exactly one space between numbers. Since v06, optional pre-filled grid values can be supplied as a second argument, using the same space-separated format. A value of `0` represents an empty cell; since v06a, `0` also represents an unspecified constraint.

The optional flag `-s <n_solutions>` controls solution enumeration. By default, the solver stops after the first solution. With `-s`, it searches until it finds the requested number of solutions or exhausts all possibilities, and prints the solutions found. The special case `-s 0` enumerates all solutions and reports their count without printing individual solution grids.

Solutions (if found) are printed like this:

```
4 9 8 3 2 1 7 6 5
6 4 7 5 1 8 3 2 9
3 2 5 4 9 7 6 8 1
2 1 6 9 4 3 8 5 7
9 5 4 1 3 6 2 7 8
1 8 3 6 7 5 4 9 2
8 7 9 2 5 4 1 3 6
5 6 1 7 8 2 9 4 3
7 3 2 8 6 9 5 1 4
```

### Instances

Additional example inputs of different sizes (more instances can be found in the benchmark datasets or generated with the Python scripts):
```
./skyscraper_solver "5 2 3 2 2 1 4 1 3 3 3 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 3"
./skyscraper_solver "2 3 4 3 1 2 3 2 3 1 3 5 4 3 2 4 3 3 4 2 2 1 4 2 3 3 1 2 5 4 2 3"
./skyscraper_solver "2 3 4 3 1 2 3 2 3 2 3 4 4 3 2 4 2 3 1 2 2 2 4 2 2 3 3 2 5 4 2 3"
./skyscraper_solver "3 1 2 3 2 3 3 3 2 3 5 2 2 3 1 2 3 4 2 4 3 3 1 3 2 5 3 5 1 3 3 2 5 2 3 3"
```

## Python Cross-Checking Solver

A Python-based Skyscraper solver using either Z3 or OR-Tools CP-SAT as its backend is available in [python_solver/](python_solver/). It provides an independent mathematical reference for cross-checking the C solver's solution counts and cell assignments.

Install its dependencies with `pip install -r python_solver/requirements.txt`, then use the scripts in that directory for reference solving and verification.

## Auxiliary Tools and Benchmarking

Alongside the C solver, [python_scripts/](python_scripts/) contains tools for generating puzzle instances, running benchmarks, comparing solver versions, and verifying correctness. The [benchmark_sets/](benchmark_sets/) and [puzzle_bank/](puzzle_bank/) directories contain instances used for testing and performance evaluation.

Since v09, benchmarking and parameter tuning have become an important part of development. In particular, the SPSA (Simultaneous Perturbation Stochastic Approximation) scripts help tune the solver's many search and pruning parameters against benchmark workloads. Related scripts analyze tuning runs and apply selected parameter values. The auxiliary tools are primarily intended for development and experimentation; they are not required to compile or use the C solver.

## Version History

### v09
Large-scale refactoring and tuning across the codebase, with agent-assisted development.
Expanded the benchmarking tools and added automated parameter tuning using SPSA.
Added CI checks to help verify correctness throughout development.

Completes the size 9 benchmark set in roughly 20 minutes on a 2.20 GHz Intel Xeon. This result is workload- and version-dependent; see earlier entries for historical comparisons.

Some regression in size 8 enumeration performance.

### v08
Added Python Z3 Cross-Checking Solver.
Added more auxiliary python scripts to measure and improve performance.
Refactored lookahead node pruning logic and integrated domain-specific type definitions and tuned parameters.

Solves the size 9 benchmark set in roughly 7:48 on a 2.20GHz Intel Xeon.

### v07
Added flag to allow searching for multiple solutions. Special case is 0, where solutions are not stored and output, instead only the number of solutions will be displayed at the end.

First version being able to solve the size 9 benchmarkset in roughly 7:59 on a 2.20GHz Intel Xeon.

### v06 / v06a / v06b
Added support for inputing grid values (v06) and empty constraint values (v06a). Changed program name in readme and benchmark scripts. Refactored and improved node pruning: Sacrificing a bit of speed for easier instances but being faster on harder ones.
Added bugfix in v06b and improved benchmarking. Bugfix has a very significant performance impact.

### v05
Solving process now sets cells as soon as only one value remains.

### v04
Added scripts to generate instances and for benchmarking. Refactored and improved constraint bound calculation slightly. Improved update of bounds / availability when marking values invalid. Added consideration of availability of values across columns / rows to the node selection heuristic.

### v03
Added arrays to keep track of cell bounds to allow more efficient calculations. Refactored node selection procedure to be more readable and maintainable. Constraint tightening now has the possibility to be iterated during early nodes to make use of cell bounds. Node selection now allows cell and value to be selected independently. Version v03 is somewhat work in progress, it regressed a lot in speed due to unecessary recalculations of constraints after trying every value instead of just once per node.

### v02 / v02a / v02b
Constraint calculation was changed to be more efficient and now takes lower and upper bounds of unset cells into consideration. Different print utilities were added to allow for easier understanding and debugging. In v02b debug prints are removed from main to reduce noisy outputs. Compared to v01 v02 is a lot faster on random 7x7 instances, but was slower on the few 9x9 example instances.

### v01
No algorithmic changes but lots of refactoring was done to clean up a few files and functions that got messy due to the projects time rectrictions as well as norminette.

### v00 / v00-fix
Submitted version for the piscine. Unfortunatly there was still a typo inside which caused invalid grids to be generated. In v00-fix this is fixed. This version also has no additional utilities and outputs the format exactly as specified in the projects subject.
