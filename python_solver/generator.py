import random
from typing import List, Dict, Tuple
from z3 import sat, Or, Not
from models import Puzzle
from solver_core import create_base_solver, create_base_solver_with_assumptions

def generate_random_latin_square(n: int) -> List[List[int]]:
    blank = Puzzle(n, {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n}, [[0]*n for _ in range(n)])
    solver, grid_vars = create_base_solver(blank, randomize=True)
    if solver.check() == sat:
        m = solver.model()
        return [[m[grid_vars[r][c]].as_long() for c in range(n)] for r in range(n)]
    raise RuntimeError("Baseline constraints tracking failure.")

def compute_all_clues(n: int, matrix: List[List[int]]) -> Dict[str, List[int]]:
    clues = {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n}
    fn = lambda line: sum(1 for i, v in enumerate(line) if v == max(line[:i+1]) and v not in line[:i])
    for i in range(n):
        clues["N"][i] = fn([matrix[r][i] for r in range(n)])
        clues["S"][i] = fn([matrix[r][i] for r in reversed(range(n))])
        clues["W"][i] = fn([matrix[i][c] for c in range(n)])
        clues["E"][i] = fn([matrix[i][c] for c in reversed(range(n))])
    return clues

def minimize_puzzle(n: int, full_clues: Dict[str, List[int]], matrix: List[List[int]], allow_grid_clues: bool = False) -> Tuple[Puzzle, bool]:
    """Removes clues, prioritizing grid clues first, returning the minimized layout and a uniqueness flag."""
    puzzle = Puzzle(n, {d: list(full_clues[d]) for d in ["N", "S", "W", "E"]},
                    [list(r) for r in matrix] if allow_grid_clues else [[0]*n for _ in range(n)])

    solver, grid_vars, lits = create_base_solver_with_assumptions(puzzle)
    active = {k: True for k in lits.keys()}

    # Verify baseline validity and uniqueness up front
    base_assumptions = [lit for lit in lits.values()]
    if solver.check(*base_assumptions) == sat:
        m = solver.model()
        solver.push()
        solver.add(Or([grid_vars[r][c] != m[grid_vars[r][c]].as_long() for r in range(n) for c in range(n)]))
        initially_unique = solver.check(*base_assumptions) != sat
        solver.pop()
    else:
        initially_unique = False

    if not initially_unique:
        return puzzle, False

    # Prioritize grid clues over edge clues
    grid_pool = [k for k in lits.keys() if k[0] == "grid"]
    edge_pool = [k for k in lits.keys() if k[0] == "edge"]
    random.shuffle(grid_pool)
    random.shuffle(edge_pool)

    for item in (grid_pool + edge_pool):
        active[item] = False
        assumptions = [lit if active[k] else Not(lit) for k, lit in lits.items()]

        if solver.check(*assumptions) == sat:
            m1 = solver.model()
            solver.push()
            solver.add(Or([grid_vars[r][c] != m1[grid_vars[r][c]].as_long() for r in range(n) for c in range(n)]))
            still_unique = solver.check(*assumptions) != sat
            solver.pop()
        else:
            still_unique = False

        if still_unique:
            if item[0] == "edge":
                puzzle.clues[item[1]][item[2]] = 0
            else:
                puzzle.grid[item[1]][item[2]] = 0
        else:
            active[item] = True

    return puzzle, True
