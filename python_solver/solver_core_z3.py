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
        _apply_visibility(s, b_grid, grid, puzzle.clues["N"][idx], [(r, idx) for r in range(n)], f"N_{idx}")
        _apply_visibility(s, b_grid, grid, puzzle.clues["S"][idx], [(r, idx) for r in reversed(range(n))], f"S_{idx}")
        _apply_visibility(s, b_grid, grid, puzzle.clues["W"][idx], [(idx, c) for c in range(n)], f"W_{idx}")
        _apply_visibility(s, b_grid, grid, puzzle.clues["E"][idx], [(idx, c) for c in reversed(range(n))], f"E_{idx}")

    return s, grid

def create_base_solver_with_assumptions(puzzle: Puzzle) -> Tuple[Solver, List[List[Int]], Dict[Tuple[str, Any, Any], Bool]]:
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

                # Apply visibility and structural bounds behind the assumption literal
                s.add(Implies(lit, _get_vis_expr_linear(s, n, b_grid, val, coords, f"{d}_{idx}")))
                for i in range(n):
                    r, c = coords[i]
                    s.add(Implies(lit, grid[r][c] <= (n - val + i + 1)))
                    if i < (val - 1):
                        s.add(Implies(lit, grid[r][c] != n))

    for r in range(n):
        for c in range(n):
            val = puzzle.grid[r][c]
            if val > 0:
                lit = Bool(f"lit_grid_{r}_{c}")
                clue_literals[("grid", r, c)] = lit
                s.add(Implies(lit, grid[r][c] == val))

    return s, grid, clue_literals

def _apply_visibility(s: Solver, b_grid: list, grid: list, val: int, coords: list, clue_id: str):
    if val > 0:
        n = len(coords)
        # Apply strict mathematical bounds to eliminate SMT branching
        for i in range(n):
            r, c = coords[i]
            s.add(grid[r][c] <= (n - val + i + 1))
            if i < (val - 1):
                s.add(grid[r][c] != n)

        s.add(_get_vis_expr_linear(s, n, b_grid, val, coords, clue_id))

def _get_vis_expr_linear(s: Solver, n: int, b_grid: list, val: int, coords: list, clue_id: str):
    flags = [1]
    running_ge = {}

    r0, c0 = coords[0]
    for h in range(1, n + 1):
        running_ge[(0, h)] = Or([b_grid[r0][c0][k] for k in range(h, n + 1)])

    for i in range(1, n):
        r_i, c_i = coords[i]
        conds = []
        for h in range(1, n + 1):
            visible_at_h = And(b_grid[r_i][c_i][h], Not(running_ge[(i - 1, h)]))
            conds.append(visible_at_h)

            cell_ge_h = Or([b_grid[r_i][c_i][k] for k in range(h, n + 1)])
            running_ge[(i, h)] = Bool(f"run_ge_{clue_id}_{i}_{h}")
            s.add(running_ge[(i, h)] == Or(running_ge[(i - 1, h)], cell_ge_h))

        flags.append(If(Or(conds), 1, 0))

    return sum(flags) == val
