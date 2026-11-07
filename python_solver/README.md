# Python reference verification

Install `requirements.txt`, then run both reference backends explicitly:

```sh
python python_solver/verify.py --backend z3
python python_solver/verify.py --backend cpsat
```

Each command exhaustively counts 20 size-7, 20 size-8, and 20 size-9 puzzles
against stored native counts. The sets have 2–4 solutions per puzzle. Each comes
from a distinct minimal-bank solution group with one edge clue removed and all
givens preserved. Source IDs, selection rules, and removed indices are recorded
in the adjacent JSON files. Size-7/8 sets are named `benchmarkSetN_python20`;
size 9 is `benchmarkSet9_minimal20`.

The verifier runs the actual CLI with an explicit backend and `-s 0`, including
Python startup in timing. A case exceeding 10 seconds, a wrong/missing count,
or a solver error fails verification. A 180-second total budget also applies.
Timeouts terminate and reap the child process. Override the budgets or provide
other sets with `--dataset PUZZLES COUNTS` (repeatable).

CI creates separate Z3 and CP-SAT matrix jobs, in parallel. They run only when
`python_solver/**` changes, including on manually forced full-suite runs: this
path guard is deliberate. Each job installs the solver dependencies, runs its
backend and verifier regression tests, and checks all 60 puzzles. Jobs have a
four-minute timeout, leaving margin for the changes and gate jobs within the
five-minute pipeline target. Runner scheduling and dependency downloads can
vary, so this is a runtime budget rather than a guarantee about queue time.

The larger native sets remain unchanged: 500 size-7 and 50 size-8 cases. On the
prepared Python 3.12 environment with two native workers, their exhaustive and
10-case finite-limit checks took 0.83s and 4.62s respectively. They are unsuitable
as the Python CI sets: a 120-second size-7 assessment reached only row 125 with
Z3 and row 217 with CP-SAT; size-8 Z3 exceeded 10s on row 1 and CP-SAT on row 15.
These were bounded assessments, not successful full Python verification runs.
