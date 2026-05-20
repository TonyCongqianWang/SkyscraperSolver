import random
from typing import List, Tuple
from z3 import Solver, Int, And, Distinct, If, sat, Or, Not, Bool
from models import Puzzle

def create_base_solver(puzzle: Puzzle, randomize: bool = False) -> Tuple[Solver, List[List[Int]]]:
    """Generates an optimized SMT solver population map mapping puzzle configurations."""
    n = puzzle.n
    s = Solver()

    if randomize:
        seed = random.randint(1, 1000000)
        s.set("random_seed", seed)
        s.set("smt.random_seed", seed)

    b_grid = [[[Bool(f"b_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    grid = [[Int(f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    # Latin Square Constraints
    for r in range(n):
        s.add(Distinct(grid[r]))
        s.add(Distinct([grid[c][r] for c in range(n)]))
        for c in range(n):
            s.add(grid[r][c] >= 1, grid[r][c] <= n)

            for h in range(1, n + 1):
                s.add(b_grid[r][c][h] == (grid[r][c] == h))

            initial_val = puzzle.grid[r][c]
            if initial_val > 0:
                s.add(grid[r][c] == initial_val)

    # Apply Visibility Clues
    for idx in range(n):
        _apply_line_visibility(s, b_grid, puzzle.clues["N"][idx], [(r, idx) for r in range(n)])
        _apply_line_visibility(s, b_grid, puzzle.clues["S"][idx], [(r, idx) for r in reversed(range(n))])
        _apply_line_visibility(s, b_grid, puzzle.clues["W"][idx], [(idx, c) for c in range(n)])
        _apply_line_visibility(s, b_grid, puzzle.clues["E"][idx], [(idx, c) for c in reversed(range(n))])

    return s, grid

def _apply_line_visibility(s: Solver, b_grid: list, clue_val: int, line_coords: List[Tuple[int, int]]):
    """Encodes line arrays visibility logic into the solver state."""
    if clue_val <= 0:
        return

    n = len(line_coords)
    vis_flags = [1]  # The first building is always visible

    for idx in range(1, n):
        curr_r, curr_c = line_coords[idx]
        cell_vis_conditions = []

        for h in range(1, n + 1):
            preceding_blocks = []
            for prev_idx in range(idx):
                p_r, p_c = line_coords[prev_idx]
                for k in range(h, n + 1):
                    preceding_blocks.append(b_grid[p_r][p_c][k])

            if preceding_blocks:
                cell_vis_conditions.append(And(b_grid[curr_r][curr_c][h], Not(Or(preceding_blocks))))
            else:
                cell_vis_conditions.append(b_grid[curr_r][curr_c][h])

        vis_flags.append(If(Or(cell_vis_conditions), 1, 0))

    s.add(sum(vis_flags) == clue_val)

def has_unique_solution(puzzle: Puzzle) -> bool:
    """Verifies that the provided setup has exactly one distinct solution matrix."""
    s, grid_vars = create_base_solver(puzzle, randomize=False)
    if s.check() != sat:
        return False

    m1 = s.model()
    n = puzzle.n
    # Add constraint forcing at least one cell value to differ
    s.add(Or([grid_vars[r][c] != m1[grid_vars[r][c]].as_long() for r in range(n) for c in range(n)]))
    return s.check() != sat
