"""Regression coverage for the optional OR-Tools reference backend."""
import importlib
from pathlib import Path
import subprocess
import sys
from typing import get_type_hints

import pytest

pytest.importorskip("ortools.sat.python.cp_model")

ROOT = Path(__file__).resolve().parents[2]
EMPTY_4 = " ".join(["0"] * 16)
TWO_SOLUTIONS = "1 3 3 0 0 0 0 2 0 0 0 0 0 0 0 0"


def test_import_annotations_and_enumeration(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "python_solver"))
    backend = importlib.import_module("solver_core_cpsat")
    from parser import parse_puzzle_input

    # Resolve annotations too, so postponing evaluation cannot mask invalid types.
    for name in ("_build_integer_grid", "_build_boolean_channeling",
                 "_apply_line_shadow_visibility", "_apply_all_visibility_clues"):
        get_type_hints(getattr(backend, name))

    puzzle = parse_puzzle_input([TWO_SOLUTIONS])
    solver, model, grid = backend.create_base_solver(puzzle)
    callback = backend.SkyscraperSolutionPrinter(grid)
    solver.parameters.enumerate_all_solutions = True
    assert solver.Solve(model, callback) == backend.cp_model.OPTIMAL
    assert len(callback.solutions) == 2
    assert len({tuple(v for row in sol for v in row)
                for sol in callback.solutions}) == 2
    for solution in callback.solutions:
        assert all(set(row) == {1, 2, 3, 4} for row in solution)
        assert all(set(col) == {1, 2, 3, 4} for col in zip(*solution))


@pytest.mark.parametrize("options,clues,count,automatic", [
    (["-b", "cpsat"], EMPTY_4, 1, False),
    (["-b", "cpsat", "-s", "2"], TWO_SOLUTIONS, 2, False),
    (["-s", "2"], TWO_SOLUTIONS, 2, True),
    (["-s", "0"], TWO_SOLUTIONS, 2, True),
])
def test_cli_backend_selection(options, clues, count, automatic):
    result = subprocess.run(
        [sys.executable, str(ROOT / "python_solver/solve_sky.py"),
         *options, clues], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert f"Total Unique Solutions Found: {count}" in result.stdout
    assert ("Auto-selected backend: cpsat" in result.stdout) == automatic
    assert result.stdout.count("--- END_OF_INSTANCE ---") == 1
