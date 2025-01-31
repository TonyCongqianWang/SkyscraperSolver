# Solver for the Skyscraper puzzle game

Created as a solution for the Rush01 Project of the C Piscine in 42 Heilbronn. Compilation and usage like this:

```
cc -Wall -Wextra -Werror -o rush-01 src/*.c
./rush-01 "5 3 2 1 3 4 1 2 4 2 2 3 4 3 2 3 2 1 3 4 2 1 2 3"
```

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

Accepts grids up to size 9. Constraints are in order top (l->r) bottom (l->r) left (t->b) right (t->b).

You can find puzzles that you can play yourself [here](https://www.puzzle-skyscrapers.com/) or [here](https://www.brainbashers.com/skyscrapers.asp).

## Instances

Some more example inputs of different sizes:
```
./rush-01 "5 2 3 2 2 1 4 1 3 3 3 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 3"
./rush-01 "5 2 3 2 2 1 4 1 3 3 3 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 2"
./rush-01 "4 2 3 2 2 1 4 1 3 3 3 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 2"
./rush-01 "4 2 3 2 2 1 4 1 3 3 2 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 2"
./rush-01 "4 2 3 2 2 1 4 1 3 3 2 4 2 2 3 3 4 2 3 2 1 2 3 2 4 3 1 2"
./rush-01 "4 2 3 2 2 2 4 2 3 3 2 3 2 2 3 3 3 2 3 2 4 2 3 2 4 3 2 2"
./rush-01 "2 3 4 3 1 2 3 2 3 1 3 5 4 3 2 4 3 3 4 2 2 1 4 2 3 3 1 2 5 4 2 3"
./rush-01 "2 3 4 3 1 2 3 2 3 1 3 5 4 3 2 4 2 3 4 2 2 1 4 2 2 3 1 2 5 4 2 3"
./rush-01 "2 3 4 3 1 2 3 2 3 1 3 4 4 3 2 4 2 3 4 2 2 1 4 2 2 3 1 2 5 4 2 3"
./rush-01 "2 3 4 3 1 2 3 2 3 1 3 4 4 3 2 3 2 3 4 2 2 1 4 2 2 3 1 2 5 4 2 3"
./rush-01 "2 3 4 3 1 2 3 2 3 1 3 4 3 3 2 4 2 3 4 2 2 1 4 2 2 3 1 2 5 4 2 3"
./rush-01 "2 3 4 3 1 2 3 2 3 2 3 4 4 3 2 4 2 3 3 2 2 2 4 2 2 3 1 2 5 4 2 3"
./rush-01 "2 3 4 3 4 2 3 2 3 2 3 4 3 3 2 4 2 3 2 2 2 2 4 2 2 3 3 2 5 4 2 3"
./rush-01 "2 3 4 3 1 2 3 2 3 2 3 4 4 3 2 4 2 3 1 2 2 2 4 2 2 3 3 2 5 4 2 3"
./rush-01 "3 2 2 3 2 3 3 3 2 3 4 2 2 3 2 2 3 4 2 4 3 3 1 3 2 4 3 4 1 3 3 2 2 2 3 3"
./rush-01 "3 1 2 3 2 3 3 3 2 3 5 2 2 3 1 2 3 4 2 4 3 3 1 3 2 5 3 5 1 3 3 2 2 2 3 3"
./rush-01 "1 4 3 3 4 3 3 2 2 4 2 3 2 1 3 2 3 3 1 4 5 2 3 2 3 2 4 2 2 2 3 4 3 1 3 5"
./rush-01 "3 1 2 3 2 3 3 3 2 3 5 2 2 3 1 2 3 4 2 4 3 3 1 3 2 5 3 5 1 3 3 2 5 2 3 3"
./rush-01 "3 1 2 3 2 3 3 3 2 3 3 2 2 3 5 2 3 3 2 4 3 3 2 3 2 3 3 3 1 4 3 2 4 2 3 2"
./rush-01 "2 4 2 3 2 2 5 3 2 3 3 2 2 3 1 2 3 3 2 3 3 3 2 2 2 3 3 3 2 4 3 2 4 1 3 2"
./rush-01 "2 4 2 3 2 2 2 3 2 3 3 2 7 3 1 2 3 3 2 3 3 3 2 2 2 3 3 3 2 4 3 2 4 1 3 2"
```


## Changes

### v00 / v00-fix
Submitted version for the piscine. Unfortunatly there was still a typo inside which caused invalid grids to be generated. In v00-fix this is fixed. This version also has no additional utilities and outputs the format exactly as specified in the projects subject.

### v01
No algorithmic changes but lots of refactoring was done to clean up a few files and functions that got messy due to the projects time rectrictions as well as norminette.

### v02
Constraint calculation was changed to be more effecient and now takes lower and upper bounds of unset cells into consideration. Different print utilities were added to allow for easier understanding and debugging.

### v03
Added arrays to keep track of cell bounds to allow more effecient calculations. Refactored node selecton procedure to be more readable and maintainable. Constraint tightening now has the possibility to be iterated during early nodes to make use of cell bounds. Node selection now allows cell and value to be selected independently. Even though v03 is significantly slower on both 9x9 instances that v01 solved. It can solve many instances a lot faster.