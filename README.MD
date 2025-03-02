# Solver for the Skyscraper puzzle game

Created as a solution for the Rush01 Project of the C Piscine in 42 Heilbronn. Compilation and usage like this (assuming cc is your C compiler):

```
cc -Wall -Wextra -Werror -O2 -o skyscraper_solver src/*.c
./skyscraper_solver "3 0 0 0 2 4 1 5 2 4 3 0 4 3 0 0 4 0 2 2 0 3 4 3 0 0 0 3 0 0 0 2" "0 0 0 0 0 0 0 1 0 0 8 0 0 2 0 0 0 0 0 5 0 0 0 0 0 0 0 1 0 0 0 0 0 0 5 3 0 0 0 0 0 0 0 2 0 0 1 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0 0 0"
./skyscraper_solver "2 3 2 4 3 2 1 5 1 3 2 3 2 4 5 4 2 3 3 2 5 3 3 1 2 4 3 2 1 2 2 5" "0 3 0 0 5 0 0 0 1 0 0 5 0 0 0 0 3 0 6 0 2 0 0 0 0 0 0 1 0 0 6 0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0 1 4 0 0 0 0 0 1 0 0"
```

or on windows:

```
.\skyscraper_solver "5 3 2 1 3 4 1 2 4 2 2 3 4 3 2 3 2 1 3 4 2 1 2 3"
```

Grids up to size 9x9 are accepted. Constraint values (aka clues) are in order top (l->r) bottom (l->r) left (t->b) right (t->b). The format has to be exactly as specified. Exacltly one space seperating each number. Since v06 grids can optionally be input as second argument (same format rules apply). Empty cells are represented by the number 0. Version v06a allows empty constraint values, also represented by 0.

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

You can find puzzles that you can play yourself [here](https://www.puzzle-skyscrapers.com/) or [here](https://www.brainbashers.com/skyscrapers.asp).

### Instances

Some more example inputs of different sizes (more can be found in the benchmark_scripts or generated automatically using the python script):
```
./skyscraper_solver "5 2 3 2 2 1 4 1 3 3 3 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 3"
./skyscraper_solver "2 3 4 3 1 2 3 2 3 1 3 5 4 3 2 4 3 3 4 2 2 1 4 2 3 3 1 2 5 4 2 3"
./skyscraper_solver "2 3 4 3 1 2 3 2 3 2 3 4 4 3 2 4 2 3 1 2 2 2 4 2 2 3 3 2 5 4 2 3"
./skyscraper_solver "3 1 2 3 2 3 3 3 2 3 5 2 2 3 1 2 3 4 2 4 3 3 1 3 2 5 3 5 1 3 3 2 5 2 3 3"
```


## Changes

### v00 / v00-fix
Submitted version for the piscine. Unfortunatly there was still a typo inside which caused invalid grids to be generated. In v00-fix this is fixed. This version also has no additional utilities and outputs the format exactly as specified in the projects subject.

### v01
No algorithmic changes but lots of refactoring was done to clean up a few files and functions that got messy due to the projects time rectrictions as well as norminette.

### v02 / v02a / v02b
Constraint calculation was changed to be more efficient and now takes lower and upper bounds of unset cells into consideration. Different print utilities were added to allow for easier understanding and debugging. In v02b debug prints are removed from main to reduce noisy outputs. Compared to v01 v02 is a lot faster on random 7x7 instances, but was slower on the few 9x9 example instances.

### v03
Added arrays to keep track of cell bounds to allow more efficient calculations. Refactored node selection procedure to be more readable and maintainable. Constraint tightening now has the possibility to be iterated during early nodes to make use of cell bounds. Node selection now allows cell and value to be selected independently. Version v03 is somewhat work in progress, it regressed a lot in speed due to unecessary recalculations of constraints after trying every value instead of just once per node.

### v04
Added scripts to generate instances and for benchmarking. Refactored and improved constraint bound calculation slightly. Improved update of bounds / availability when marking values invalid. Added consideration of availability of values across columns / rows to the node selection heuristic.

### v05
Solving process now sets cells as soon as only one value remains.

### v06 / v06a / v06b
Added support for inputing grid values (v06) and empty constraint values (v06a). Changed program name in readme and benchmark scripts. Refactored and improved node pruning: Sacrificing a bit of speed for easier instances but being faster on harder ones.
Added bugfix in v06b and improved benchmarking. Bugfix has a very significant performance impact.

## Future
- Make the puzzle playable: Formulate solution process as mdp, add GUI and train an AI player with Reinforcement learning.
- Possibly reimplementation in Python or C#.
