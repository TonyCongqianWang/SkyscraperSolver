import math
import random
from typing import List, Tuple, Dict, Any
from z3 import Solver, Int, And, Distinct, If, Or, Not, Bool, Implies
from models import Puzzle

def _build_core_model(n: int, randomize: bool = False) -> Tuple[Solver, List[List[Int]], List[List[List[Bool]]]]:
    """Helper: Initializes the core Latin Square and Pigeonhole structures."""
    s = Solver()
    if randomize:
        seed = random.randint(1, 1000000)
        s.set("random_seed", seed)
        s.set("smt.random_seed", seed)

    b_grid = [[[Bool(f"b_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    grid = [[Int(f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    # 1. Base Latin Square Constraints
    for r in range(n):
        s.add(Distinct(grid[r]))
        s.add(Distinct([grid[c][r] for c in range(n)]))
        for c in range(n):
            s.add(grid[r][c] >= 1, grid[r][c] <= n)
            for h in range(1, n + 1):
                s.add(b_grid[r][c][h] == (grid[r][c] == h))

    # 2. Sudoku Pigeonhole Injections (Hidden Single Accelerators)
    for r in range(n):
        for h in range(1, n + 1):
            s.add(Or([b_grid[r][c][h] for c in range(n)]))
            s.add(Or([b_grid[c][r][h] for c in range(n)]))

    box_size = int(math.sqrt(n))
    if box_size * box_size == n:
        for b_r in range(box_size):
            for b_c in range(box_size):
                for h in range(1, n + 1):
                    s.add(Or([b_grid[r][c][h] for r in range(b_r * box_size, (b_r + 1) * box_size)
                                              for c in range(b_c * box_size, (b_c + 1) * box_size)]))

    return s, grid, b_grid


def _apply_structural_visibility(s: Solver, n: int, b_grid: List[List[List[Bool]]]) -> Dict[Tuple[str, int], Tuple[List, List[Bool]]]:
    """Helper: Applies the Tseytin transformation (Prefix Shadows) and generalized visibility invariants."""
    # Pre-calculate "Greater Than or Equal" variables to keep clauses small
    ge_grid = [[[Bool(f"ge_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            for h in range(1, n + 1):
                s.add(ge_grid[r][c][h] == Or([b_grid[r][c][k] for k in range(h, n + 1)]))

    directions = {
        "N": lambda idx: [(r, idx) for r in range(n)],
        "S": lambda idx: [(r, idx) for r in reversed(range(n))],
        "W": lambda idx: [(idx, c) for c in range(n)],
        "E": lambda idx: [(idx, c) for c in reversed(range(n))]
    }

    vis_profiles = {}

    for d, coord_func in directions.items():
        for idx in range(n):
            coords = coord_func(idx)

            # v_bits: Is the building at step i visible?
            vis_bits = [Bool(f"v_{d}_{idx}_{i}") for i in range(n)]

            # shadow_bits[i][h]: Is the max height from step 0 to i >= h?
            shadow = [[Bool(f"shadow_{d}_{idx}_{i}_h{h}") for h in range(n + 1)] for i in range(n)]

            # Base Case: Step 0
            s.add(vis_bits[0] == True)
            r0, c0 = coords[0]
            for h in range(1, n + 1):
                s.add(shadow[0][h] == ge_grid[r0][c0][h])

            # Recursive Chain: Step i depends ONLY on Step i-1
            for i in range(1, n):
                r_i, c_i = coords[i]

                # 1. Update the Shadow domino chain
                for h in range(1, n + 1):
                    s.add(shadow[i][h] == Or(shadow[i-1][h], ge_grid[r_i][c_i][h]))

                # 2. Building is visible if its height h is strictly greater than the shadow at i-1
                vis_conditions = []
                for h in range(1, n + 1):
                    vis_conditions.append(And(b_grid[r_i][c_i][h], Not(shadow[i-1][h])))
                s.add(vis_bits[i] == Or(vis_conditions))

            # --- GENERALIZATION 1: The Max-Shadow Rule ---
            # If the shadow reaches N at step i, nothing after i is visible
            for i in range(n - 1):
                for j in range(i + 1, n):
                    s.add(Implies(shadow[i][n], Not(vis_bits[j])))

            # --- GENERALIZATION 2: Remaining Vision Capping Rules ---
            for i in range(n - 1):
                r, c = coords[i]
                for h in range(1, n + 1):
                    remaining_slots = n - 1 - i
                    max_remaining_vision = n - h
                    if max_remaining_vision < remaining_slots:
                        s.add(Implies(
                            b_grid[r][c][h],
                            sum([If(vis_bits[j], 1, 0) for j in range(i + 1, n)]) <= max_remaining_vision
                        ))

            vis_profiles[(d, idx)] = (coords, vis_bits)

    return vis_profiles


def create_base_solver(puzzle: Puzzle, randomize: bool = False) -> Tuple[Solver, List[List[Int]]]:
    """Generates a standalone Z3 solver optimized for raw speed via direct constraints."""
    s, grid, b_grid = _build_core_model(puzzle.n, randomize)

    # Force preset clues into the base matrix immediately
    for r in range(puzzle.n):
        for c in range(puzzle.n):
            if puzzle.grid[r][c] > 0:
                s.add(grid[r][c] == puzzle.grid[r][c])

    vis_profiles = _apply_structural_visibility(s, puzzle.n, b_grid)

    # Bind the specific target values as direct un-gated constraints
    for d in ["N", "S", "W", "E"]:
        for idx in range(puzzle.n):
            k = puzzle.clues[d][idx]
            if k > 0:
                coords, vis_bits = vis_profiles[(d, idx)]
                s.add(sum([If(vis_bits[i], 1, 0) for i in range(puzzle.n)]) == k)

    return s, grid


def create_base_solver_with_assumptions(puzzle: Puzzle) -> Tuple[Solver, List[List[Int]], Dict[Tuple[str, Any, Any, Any], Bool]]:
    """Generates a warm incremental solver core ready for batched assumption toggles."""
    s, grid, b_grid = _build_core_model(puzzle.n, False)

    # Store references for later dynamic gating
    s._b_grid = b_grid
    s._vis_profiles = _apply_structural_visibility(s, puzzle.n, b_grid)

    clue_literals = {}
    add_puzzle_clues_to_assumptions(s, grid, puzzle, clue_literals)
    return s, grid, clue_literals


def add_puzzle_clues_to_assumptions(s: Solver, grid: List[List[Int]], puzzle: Puzzle, clue_literals: dict):
    """Dynamically links value-aware clue activations to the underlying structural visibility bits."""
    n = puzzle.n

    for d in ["N", "S", "W", "E"]:
        for idx in range(n):
            val = puzzle.clues[d][idx]
            if val > 0:
                key = ("edge", d, idx, val)
                if key not in clue_literals:
                    lit = Bool(f"lit_edge_{d}_{idx}_v{val}")
                    clue_literals[key] = lit
                    coords, vis_bits = s._vis_profiles[(d, idx)]
                    s.add(Implies(lit, sum([If(vis_bits[i], 1, 0) for i in range(n)]) == val))

    for r in range(n):
        for c in range(n):
            val = puzzle.grid[r][c]
            if val > 0:
                key = ("grid", r, c, val)
                if key not in clue_literals:
                    lit = Bool(f"lit_grid_{r}_{c}_v{val}")
                    clue_literals[key] = lit
                    s.add(Implies(lit, grid[r][c] == val))
