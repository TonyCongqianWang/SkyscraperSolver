import math
from typing import List, Tuple, Dict, Any
from z3 import Solver, Int, And, Distinct, If, Or, Not, Bool, Implies
from models import Puzzle


def create_base_solver(puzzle: Puzzle, randomize: bool = False) -> Tuple[Solver, List[List[Int]]]:
    """Generates a standalone Z3 solver instance optimized with pigeonhole
    and generalized visibility physics (Shadow & Capping rules).
    """
    s = Solver()
    if randomize:
        import random
        seed = random.randint(1, 1000000)
        s.set("random_seed", seed)
        s.set("smt.random_seed", seed)

    n = puzzle.n
    b_grid = [[[Bool(f"b_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    grid = [[Int(f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    # 1. Base Latin Square Engine
    for r in range(n):
        s.add(Distinct(grid[r]))
        s.add(Distinct([grid[c][r] for c in range(n)]))
        for c in range(n):
            s.add(grid[r][c] >= 1, grid[r][c] <= n)
            for h in range(1, n + 1):
                s.add(b_grid[r][c][h] == (grid[r][c] == h))
            if puzzle.grid[r][c] > 0:
                s.add(grid[r][c] == puzzle.grid[r][c])

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

    # 3. Structural Visibility Tracking & Physical Invariants
    directions = {
        "N": lambda idx: [(r, idx) for r in range(n)],
        "S": lambda idx: [(r, idx) for r in reversed(range(n))],
        "W": lambda idx: [(idx, c) for c in range(n)],
        "E": lambda idx: [(idx, c) for c in reversed(range(n))]
    }

    for d, coord_func in directions.items():
        for idx in range(n):
            k = puzzle.clues[d][idx]
            if k > 0:
                coords = coord_func(idx)
                vis_bits = [Bool(f"v_{d}_{idx}_{i}") for i in range(n)]
                s.add(vis_bits[0] == True)  # First item is always visible

                # Link visibility tracking bits to relative cell heights
                for i in range(1, n):
                    preceding_cells_shorter = []
                    for p_idx in range(i):
                        for h_curr in range(1, n + 1):
                            shorter_conds = [b_grid[coords[p_idx][0]][coords[p_idx][1]][h_pre] for h_pre in range(h_curr, n + 1)]
                            preceding_cells_shorter.append(
                                Implies(b_grid[coords[i][0]][coords[i][1]][h_curr], Not(Or(shorter_conds)))
                            )
                    s.add(vis_bits[i] == And(preceding_cells_shorter))

                # Direct target sum constraint
                s.add(sum([If(vis_bits[i], 1, 0) for i in range(n)]) == k)

                # --- GENERALIZATION 1: The Max-Shadow Rule ---
                for i in range(n - 1):
                    r, c = coords[i]
                    for j in range(i + 1, n):
                        s.add(Implies(b_grid[r][c][n], Not(vis_bits[j])))

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

    return s, grid


def create_base_solver_with_assumptions(puzzle: Puzzle) -> Tuple[Solver, List[List[Int]], Dict[Tuple[str, Any, Any, Any], Bool]]:
    """Generates a warm incremental solver core with generalized visibility logic bound to literal toggles."""
    n = puzzle.n
    s = Solver()

    # Keep the boolean grid references in the solver context for dynamic access
    s._b_grid = [[[Bool(f"b_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    grid = [[Int(f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    # 1. Permanent Latin Square Rules
    for r in range(n):
        s.add(Distinct(grid[r]))
        s.add(Distinct([grid[c][r] for c in range(n)]))
        for c in range(n):
            s.add(grid[r][c] >= 1, grid[r][c] <= n)
            for h in range(1, n + 1):
                s.add(s._b_grid[r][c][h] == (grid[r][c] == h))

    # 2. Permanent Sudoku Pigeonhole Injections
    for r in range(n):
        for h in range(1, n + 1):
            s.add(Or([s._b_grid[r][c][h] for c in range(n)]))
            s.add(Or([s._b_grid[c][r][h] for c in range(n)]))

    box_size = int(math.sqrt(n))
    if box_size * box_size == n:
        for b_r in range(box_size):
            for b_c in range(box_size):
                for h in range(1, n + 1):
                    s.add(Or([s._b_grid[r][c][h] for r in range(b_r * box_size, (b_r + 1) * box_size)
                                              for c in range(b_c * box_size, (b_c + 1) * box_size)]))

    # 3. Permanent Physical Visibility Foundations (Structural tracking bits)
    s._vis_profiles = {}
    directions = {
        "N": lambda idx: [(r, idx) for r in range(n)],
        "S": lambda idx: [(r, idx) for r in reversed(range(n))],
        "W": lambda idx: [(idx, c) for c in range(n)],
        "E": lambda idx: [(idx, c) for c in reversed(range(n))]
    }

    for d, coord_func in directions.items():
        for idx in range(n):
            coords = coord_func(idx)
            vis_bits = [Bool(f"v_{d}_{idx}_{i}") for i in range(n)]
            s.add(vis_bits[0] == True)  # First item is always visible

            # Tie the visibility bits to the structural properties of the cell heights
            for i in range(1, n):
                preceding_cells_shorter = []
                for p_idx in range(i):
                    for h_curr in range(1, n + 1):
                        shorter_conds = [s._b_grid[coords[p_idx][0]][coords[p_idx][1]][h_pre] for h_pre in range(h_curr, n + 1)]
                        preceding_cells_shorter.append(
                            Implies(s._b_grid[coords[i][0]][coords[i][1]][h_curr], Not(Or(shorter_conds)))
                        )
                s.add(vis_bits[i] == And(preceding_cells_shorter))

            # Store the bit vectors for live implication wiring during the batch passes
            s._vis_profiles[(d, idx)] = (coords, vis_bits)

            # --- GENERALIZATION 1: The Max-Shadow Rule (Structural & Permanent) ---
            for i in range(n - 1):
                r, c = coords[i]
                for j in range(i + 1, n):
                    s.add(Implies(s._b_grid[r][c][n], Not(vis_bits[j])))

            # --- GENERALIZATION 2: Remaining Vision Capping Rules (Structural & Permanent) ---
            for i in range(n - 1):
                r, c = coords[i]
                for h in range(1, n + 1):
                    remaining_slots = n - 1 - i
                    max_remaining_vision = n - h
                    if max_remaining_vision < remaining_slots:
                        s.add(Implies(
                            s._b_grid[r][c][h],
                            sum([If(vis_bits[j], 1, 0) for j in range(i + 1, n)]) <= max_remaining_vision
                        ))

    clue_literals = {}
    # Run the initial instance mapping directly upon construction
    add_puzzle_clues_to_assumptions(s, grid, puzzle, clue_literals)
    return s, grid, clue_literals


def add_puzzle_clues_to_assumptions(s: Solver, grid: List[List[Int]], puzzle: Puzzle, clue_literals: dict):
    """Dynamically links value-aware clue activations to the underlying structural visibility bits."""
    n = puzzle.n

    for d in ["N", "S", "W", "E"]:
        for idx in range(n):
            val = puzzle.clues[d][idx]
            if val > 0:
                # Value-specific tracking key ensures cross-puzzle execution safety
                key = ("edge", d, idx, val)
                if key not in clue_literals:
                    lit = Bool(f"lit_edge_{d}_{idx}_v{val}")
                    clue_literals[key] = lit

                    # Extract the pre-compiled structural tracking bits for this lane
                    coords, vis_bits = s._vis_profiles[(d, idx)]

                    # Wire the activation gate: If lit is True, the visibility bit sum MUST equal val
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
