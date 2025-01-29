### Solver for the Skyscraper puzzle game

Created as a solution for the Rush01 Project of the C Piscine in 42 Heilbronn.

```
cc -Wall -Wextra -Werror -o rush-01 src/*.c
./rush-01 '4 1 2 2 1 4 2 2 2 3 2 1 2 1 2 3'
./rush-01 "5 3 2 1 3 4 1 2 4 2 2 3 4 3 2 3 2 1 3 4 2 1 2 3"
./rush-01 "5 2 3 2 2 1 4 1 3 3 3 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 3"
./rush-01 "2 3 4 3 1 2 3 2 3 1 3 5 4 3 2 4 2 3 4 2 2 1 4 2 2 3 1 2 5 4 2 3"
./rush-01 "3 1 2 3 2 3 3 3 2 3 5 2 2 3 1 2 3 4 2 4 3 3 1 3 2 5 3 5 1 3 3 2 2 2 3 3"
./rush-01 "1 4 3 3 4 3 3 2 2 4 2 3 2 1 3 2 3 3 1 4 5 2 3 2 3 2 4 2 2 2 3 4 3 1 3 5"
./rush-01 "3 1 2 3 2 3 3 3 2 3 5 2 2 3 1 2 3 4 2 4 3 3 1 3 2 5 3 5 1 3 3 2 5 2 3 3"
```

Accepts grids up to size 9. Constraints are in order top (l->r) bottom (l->r) left (t->b) right (t->b).

You can find puzzles that you can play yourself [here](https://www.puzzle-skyscrapers.com/) or [here](https://www.brainbashers.com/skyscrapers.asp) .