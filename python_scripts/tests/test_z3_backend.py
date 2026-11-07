"""Skyscraper Latin squares must not acquire Sudoku box constraints."""
from pathlib import Path
import subprocess
import sys

import pytest

z3 = pytest.importorskip("z3")
ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("n", [4, 9])
@pytest.mark.parametrize("incremental", [False, True])
def test_non_sudoku_latin_square(monkeypatch, n, incremental):
    monkeypatch.syspath_prepend(str(ROOT / "python_solver"))
    from models import Puzzle
    from solver_core_z3 import (create_base_solver,
                                create_base_solver_with_assumptions)

    # Cyclic Latin squares have repeated values inside the would-be Sudoku boxes.
    solution = [[(r + c) % n + 1 for c in range(n)] for r in range(n)]
    puzzle = Puzzle(n, {d: [0] * n for d in "NSWE"}, solution)
    if incremental:
        solver, grid, literals = create_base_solver_with_assumptions(puzzle)
        status = solver.check(*literals.values())
    else:
        solver, grid = create_base_solver(puzzle)
        status = solver.check()
    assert status == z3.sat
    model = solver.model()
    assert [[model[cell].as_long() for cell in row] for row in grid] == solution


def test_empty_four_by_four_count():
    result = subprocess.run(
        [sys.executable, str(ROOT / "python_solver/solve_sky.py"),
         "-b", "z3", "-s", "0", " ".join(["0"] * 16)],
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "Total Unique Solutions Found: 576" in result.stdout


def test_automatic_single_solution_without_sudoku_boxes():
    solution = " ".join(str((r + c) % 4 + 1)
                        for r in range(4) for c in range(4))
    result = subprocess.run(
        [sys.executable, str(ROOT / "python_solver/solve_sky.py"),
         " ".join(["0"] * 16), solution],
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "Auto-selected backend: z3" in result.stdout
    assert "Total Unique Solutions Found: 1" in result.stdout
