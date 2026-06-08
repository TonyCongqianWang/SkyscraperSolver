import random
from typing import List, Tuple, Dict
from z3 import Solver, Int, And, Distinct, If, Or, Not, Bool, Implies
from models import Puzzle

def _get_structural_bounds_expr(grid: list, n: int, val: int, coords: list) -> List:
    exprs = []
    for i in range(len(coords)):
        r, c = coords[i]
        exprs.append(grid[r][c] <= (n - val + i + 1))
        if i < (val - 1):
            exprs.append(grid[r][c] != n)
    return exprs

def _get_vis_expr_z3(n: int, b_grid: list, val: int, coords: list):
    flags = [1]
    for idx in range(1, n):
        conds = []
        for h in range(1, n + 1):
            pre = [b_grid[p_r][p_c][k] for p_idx in range(idx) for p_r, p_c in [coords[p_idx]] for k in range(h, n + 1)]
            conds.append(And(b_grid[coords[idx][0]][coords[idx][1]][h], Not(Or(pre))) if pre else b_grid[coords[idx][0]][coords[idx][1]][h])
        flags.append(If(Or(conds), 1, 0))
    return sum(flags) == val

def create_base_solver_with_assumptions(n: int) -> Tuple[Solver, List[List[Int]], Dict]:
    """Generates a generic Z3 solver for ANY puzzle of size N, mapped to assumption literals."""
    s = Solver()
    b_grid = [[[Bool(f"b_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    grid = [[Int(f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    # Latin Square constraints
    for r in range(n):
        s.add(Distinct(grid[r]))
        s.add(Distinct([grid[c][r] for c in range(n)]))
        for c in range(n):
            s.add(grid[r][c] >= 1, grid[r][c] <= n)
            for h in range(1, n + 1):
                s.add(b_grid[r][c][h] == (grid[r][c] == h))

    clue_literals = {}

    # 1. Edge Clue Literals (Pre-compile all possible values for all edges)
    for d in ["N", "S", "W", "E"]:
        for idx in range(n):
            coords = ([(r, idx) for r in range(n)] if d == "N" else
                      [(r, idx) for r in reversed(range(n))] if d == "S" else
                      [(idx, c) for c in range(n)] if d == "W" else [(idx, c) for c in reversed(range(n))])
            for val in range(1, n + 1):
                lit = Bool(f"lit_edge_{d}_{idx}_v{val}")
                clue_literals[("edge", d, idx, val)] = lit

                # FIX: Both structural bounds and visibility calculations are now correctly guarded behind the literal
                bounds_exprs = _get_structural_bounds_expr(grid, n, val, coords)
                for expr in bounds_exprs:
                    s.add(Implies(lit, expr))
                s.add(Implies(lit, _get_vis_expr_z3(n, b_grid, val, coords)))

    # 2. Grid Given Literals
    for r in range(n):
        for c in range(n):
            for val in range(1, n + 1):
                lit = Bool(f"lit_grid_{r}_{c}_v{val}")
                clue_literals[("grid", r, c, val)] = lit
                s.add(Implies(lit, grid[r][c] == val))

    return s, grid, clue_literals

def create_base_solver(puzzle: Puzzle, randomize: bool = False) -> Tuple[Solver, List[List[Int]]]:
    s, grid, clue_literals = create_base_solver_with_assumptions(puzzle.n)
    if randomize:
        seed = random.randint(1, 1000000)
        s.set("random_seed", seed)
        s.set("smt.random_seed", seed)

    for d, idx, val in puzzle.get_active_clues():
        s.add(clue_literals[("edge", d, idx, val)] == True)
    for r, c, val in puzzle.get_active_grid_given():
        s.add(clue_literals[("grid", r, c, val)] == True)

    return s, grid
