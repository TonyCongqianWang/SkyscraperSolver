### Solver for the Skyscraper puzzle game

Made during the Rush01 of the C Piscine in 42 Heilbronn. Compile and use as following;

```
cc -Wall -Wextra -Werror -o rush-01 *.c
./rush-01 "5 2 3 2 2 1 4 1 3 3 3 4 2 2 3 3 4 2 2 2 1 2 3 2 4 3 1 3"
```

Accepts grids up to size 9. Constraints are in order top (l->r) bottom (l->r) left (t->b) right (t->b).