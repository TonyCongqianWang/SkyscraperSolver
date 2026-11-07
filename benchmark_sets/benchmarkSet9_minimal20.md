# Size-9 verification set

`benchmarkSet9_minimal20.txt` contains 20 variants from distinct solution groups
in `puzzle_bank/unique/v1/minimal/size_9.json`. Each original was checked unique
with native `-s 2`. Each variant removes one active perimeter clue, preserves all
given cells, and has 2–4 solutions. The source bank remains unchanged.

Groups are considered in order of their first puzzle's native `nodes_visited`,
then group ID. Active edge clues are tried in index order. Retain the first
variant per group with 2–4 exhaustive solutions that both Python CLIs solve in
under four seconds, until 20 pass. This timing-based acceptance can vary across
machines. `benchmarkSet9_minimal20.json` records the selected source IDs, removed
zero-based clue indices (N, S, W, E order), and counts.

Each line quotes two sequences separately: 36 perimeter clues and 81 given
cells. `_num_solutions_benchmarkSet9_minimal20.txt` contains exhaustive counts
matched by native C, explicit Z3, and explicit CP-SAT. These replace the earlier
variants that were too expensive for Z3.

The set is included in default `make test`, which checks exhaustive counts,
a limit of 10, and each puzzle's exact count. Python CI checks exhaustive counts
with hard time limits; see [Python verification](../python_solver/README.md).

```sh
python python_scripts/verify_consistency.py \
  benchmark_sets/benchmarkSet9_minimal20.txt \
  -e benchmark_sets/_num_solutions_benchmarkSet9_minimal20.txt
```
