import random
from typing import List, Dict
from z3 import Solver, sat
from models import Puzzle
from solver_core import create_base_solver, has_unique_solution

def generate_random_latin_square(n: int) -> List[List[int]]:
    """Generates a complete, verified valid Latin Square configuration grid."""
    blank_puzzle = Puzzle(n, {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n}, [[0]*n for _ in range(n)])
    solver, grid_vars = create_base_solver(blank_puzzle, randomize=True)

    cells = [(r, c) for r in range(n) for c in range(n)]
    random.shuffle(cells)

    for r, c in cells:
        s_tmp = Solver()
        s_tmp.add(solver.assertions())
        if s_tmp.check() == sat:
            val = s_tmp.model()[grid_vars[r][c]].as_long()
            solver.push()
            solver.add(grid_vars[r][c] == val)
            if solver.check() != sat:
                solver.pop()
        else:
            break

    if solver.check() == sat:
        model = solver.model()
        return [[model[grid_vars[r][c]].as_long() for c in range(n)] for r in range(n)]
    raise RuntimeError("Base initialization array split.")

def compute_all_clues(n: int, matrix: List[List[int]]) -> Dict[str, List[int]]:
    """Calculates exact line-of-sight visual clue counts for a solid grid layout."""
    clues = {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n}

    def count_line(line: List[int]) -> int:
        highest, visible = 0, 0
        for item in line:
            if item > highest:
                visible += 1
                highest = item
        return visible

    for i in range(n):
        clues["N"][i] = count_line([matrix[r][i] for r in range(n)])
        clues["S"][i] = count_line([matrix[r][i] for r in reversed(range(n))])
        clues["W"][i] = count_line([matrix[i][c] for c in range(n)])
        clues["E"][i] = count_line([matrix[i][c] for c in reversed(range(n))])
    return clues

def minimize_puzzle(n: int, full_clues: Dict[str, List[int]], matrix: List[List[int]], allow_grid_clues: bool = False) -> Puzzle:
    """Removes clues iteratively while verifying the uniqueness of the solution."""
    puzzle = Puzzle(
        n=n,
        clues={d: list(full_clues[d]) for d in ["N", "S", "W", "E"]},
        initial_grid=[[0]*n for _ in range(n)]
    )

    clue_pool = [("edge", d, idx) for d in ["N", "S", "W", "E"] for idx in range(n)]
    if allow_grid_clues:
        puzzle.grid = [list(row) for row in matrix]
        clue_pool.extend([("grid", r, c) for r in range(n) for c in range(n)])

    random.shuffle(clue_pool)

    for item in clue_pool:
        if item[0] == "edge":
            _, direction, idx = item
            saved_val = puzzle.clues[direction][idx]
            puzzle.clues[direction][idx] = 0
            if not has_unique_solution(puzzle):
                puzzle.clues[direction][idx] = saved_val
        else:
            _, r, c = item
            saved_val = puzzle.grid[r][c]
            puzzle.grid[r][c] = 0
            if not has_unique_solution(puzzle):
                puzzle.grid[r][c] = saved_val

    return puzzle
