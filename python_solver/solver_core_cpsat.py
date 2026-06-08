import random
from typing import Tuple, List, Dict, Any
from ortools.sat.python import cp_model
from models import Puzzle

def create_base_solver(puzzle: Puzzle, randomize: bool = False) -> Tuple[cp_model.CpSolver, cp_model.CpModel, List[List[cp_model.IntVar]]]:
    """Generates an OR-Tools CP-SAT instance using Lazy Clause Generation."""
    model = cp_model.CpModel()
    n = puzzle.n
    grid = [[model.NewIntVar(1, n, f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    for r in range(n):
        model.AddAllDifferent(grid[r])
        model.AddAllDifferent([grid[c][r] for c in range(n)])

    for r in range(n):
        for c in range(n):
            if puzzle.grid[r][c] > 0:
                model.Add(grid[r][c] == puzzle.grid[r][c])

    for idx in range(n):
        _apply_visibility_cpsat(model, n, grid, puzzle.clues["N"][idx], [(r, idx) for r in range(n)])
        _apply_visibility_cpsat(model, n, grid, puzzle.clues["S"][idx], [(r, idx) for r in reversed(range(n))])
        _apply_visibility_cpsat(model, n, grid, puzzle.clues["W"][idx], [(idx, c) for c in range(n)])
        _apply_visibility_cpsat(model, n, grid, puzzle.clues["E"][idx], [(idx, c) for c in reversed(range(n))])

    solver = cp_model.CpSolver()
    if randomize:
        solver.parameters.random_seed = random.randint(1, 1000000)

    return solver, model, grid

def _apply_visibility_cpsat(model: cp_model.CpModel, n: int, grid: List[List[cp_model.IntVar]], clue_val: int, coords: list):
    if clue_val <= 0:
        return

    # Add structural pruning explicitly (CP-SAT bounds tightening)
    for i in range(n):
        r, c = coords[i]
        model.Add(grid[r][c] <= (n - clue_val + i + 1))
        if i < (clue_val - 1):
            model.Add(grid[r][c] != n)

    visibility_flags = []
    r0, c0 = coords[0]
    running_max = grid[r0][c0]

    for i in range(1, n):
        r, c = coords[i]
        current_cell = grid[r][c]

        is_visible = model.NewBoolVar(f"vis_{r}_{c}")
        model.Add(current_cell > running_max).OnlyEnforceIf(is_visible)
        model.Add(current_cell <= running_max).OnlyEnforceIf(is_visible.Not())
        visibility_flags.append(is_visible)

        next_max = model.NewIntVar(1, n, f"max_{r}_{c}")
        # CORRECTED: Use AddMaxEquality instead of AddMaxEq
        model.AddMaxEquality(next_max, [running_max, current_cell])
        running_max = next_max

    model.Add(sum(visibility_flags) == (clue_val - 1))
