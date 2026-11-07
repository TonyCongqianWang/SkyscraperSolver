# Size-9 verification set

`benchmarkSet9_minimal20.txt` contains 20 variants from distinct solution groups
in `puzzle_bank/unique/v1/minimal/size_9.json`. The original puzzles were checked
unique with native `-s 2`. Each variant removes one or two active perimeter clues
and preserves all given cells. These variants intentionally have multiple
solutions; they are no longer minimal unique puzzles.

Selection is deterministic: take the first puzzle from each of the first 20
groups, removing the first active clue on odd-numbered rows and the first two on
even rows. Row 18 removes only one: the two-clue variant exceeded a 30-second
CP-SAT enumeration limit. `benchmarkSet9_minimal20.json` records the source IDs,
removed zero-based clue indices, and exact solution counts. Edge order is
N, S, W, E. The source bank is not modified.

Each input line quotes two sequences separately: 36 perimeter clues and 81 given
cells. `_num_solutions_benchmarkSet9_minimal20.txt` contains the corresponding
exhaustive counts, independently matched by native C and OR-Tools CP-SAT
9.15.6755 (all CP-SAT runs completed with `OPTIMAL` status).

The set is included in default `make test` verification. To check it alone:

```sh
python python_scripts/verify_consistency.py \
  benchmark_sets/benchmarkSet9_minimal20.txt \
  -e benchmark_sets/_num_solutions_benchmarkSet9_minimal20.txt
```

This runs exhaustive enumeration, a limit of 10, and each puzzle's exact count.
