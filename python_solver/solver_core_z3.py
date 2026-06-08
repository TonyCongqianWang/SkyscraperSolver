import random
from typing import List, Tuple, Dict, Any
from z3 import Solver, Int, And, Distinct, If, sat, Or, Not, Bool, Implies
from models import Puzzle

def create_base_solver(puzzle: Puzzle, randomize: bool = False) -> Tuple[Solver, List[List[Int]]]:
    """Generates a standard standalone Z3 solver instance."""
    s = Solver()
    if randomize:
        seed = random.randint(1, 1000000)
        s.set("random_seed", seed)
        s.set("smt.random_seed", seed)

    n = puzzle.n
    b_grid = [[[Bool(f"b_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    grid = [[Int(f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    for r in range(n):
        s.add(Distinct(grid[r]))
        s.add(Distinct([grid[c][r] for c in range(n)]))
        for c in range(n):
            s.add(grid[r][c] >= 1, grid[r][c] <= n)
            for h in range(1, n + 1):
                s.add(b_grid[r][c][h] == (grid[r][c] == h))
            if puzzle.grid[r][c] > 0:
                s.add(grid[r][c] == puzzle.grid[r][c])

    for idx in range(n):
        _apply_visibility(s, b_grid, puzzle.clues["N"][idx], [(r, idx) for r in range(n)])
        _apply_visibility(s, b_grid, puzzle.clues["S"][idx], [(r, idx) for r in reversed(range(n))])
        _apply_visibility(s, b_grid, puzzle.clues["W"][idx], [(idx, c) for c in range(n)])
        _apply_visibility(s, b_grid, puzzle.clues["E"][idx], [(idx, c) for c in reversed(range(n))])

    return s, grid

def create_base_solver_with_assumptions(puzzle: Puzzle) -> Tuple[Solver, List[List[Int]], Dict[Tuple[str, Any, Any], Bool]]:
    """Generates a solver alongside independent constraint literal activation keys."""
    n = puzzle.n
    s = Solver()
    b_grid = [[[Bool(f"b_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    grid = [[Int(f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    for r in range(n):
        s.add(Distinct(grid[r]))
        s.add(Distinct([grid[c][r] for c in range(n)]))
        for c in range(n):
            s.add(grid[r][c] >= 1, grid[r][c] <= n)
            for h in range(1, n + 1):
                s.add(b_grid[r][c][h] == (grid[r][c] == h))

    clue_literals = {}
    for d in ["N", "S", "W", "E"]:
        for idx in range(n):
            val = puzzle.clues[d][idx]
            if val > 0:
                lit = Bool(f"lit_edge_{d}_{idx}")
                clue_literals[("edge", d, idx)] = lit
                coords = ([(r, idx) for r in range(n)] if d == "N" else
                          [(r, idx) for r in reversed(range(n))] if d == "S" else
                          [(idx, c) for c in range(n)] if d == "W" else [(idx, c) for c in reversed(range(n))])
                s.add(Implies(lit, _get_vis_expr(n, b_grid, val, coords)))

    for r in range(n):
        for c in range(n):
            val = puzzle.grid[r][c]
            if val > 0:
                lit = Bool(f"lit_grid_{r}_{c}")
                clue_literals[("grid", r, c)] = lit
                s.add(Implies(lit, grid[r][c] == val))

    return s, grid, clue_literals

def _apply_visibility(s: Solver, b_grid: list, val: int, coords: list):
    if val > 0:
        s.add(_get_vis_expr(len(coords), b_grid, val, coords))

def _get_vis_expr(n: int, b_grid: list, val: int, coords: list):
    flags = [1]
    for idx in range(1, n):
        conds = []
        for h in range(1, n + 1):
            pre = [b_grid[p_r][p_c][k] for p_idx in range(idx) for p_r, p_c in [coords[p_idx]] for k in range(h, n + 1)]
            conds.append(And(b_grid[coords[idx][0]][coords[idx][1]][h], Not(Or(pre))) if pre else b_grid[coords[idx][0]][coords[idx][1]][h])
        flags.append(If(Or(conds), 1, 0))
    return sum(flags) == val
