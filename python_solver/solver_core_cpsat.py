from typing import Tuple, List, Dict
from ortools.sat.python import cp_model
from models import Puzzle


class SkyscraperSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Unified callback hook."""
    def __init__(self, grid_vars, limit=0):
        super().__init__()
        self._grid_vars = grid_vars
        self._limit = limit
        self.solutions = []

    def on_solution_callback(self):
        n = len(self._grid_vars)
        sol = [[self.Value(self._grid_vars[r][c]) for c in range(n)] for r in range(n)]
        self.solutions.append(sol)
        if self._limit > 0 and len(self.solutions) >= self._limit:
            self.StopSearch()


def _build_integer_grid(model: cp_model.CpModel, puzzle: Puzzle) -> List[List[cp_model.IntVar]]:
    """Creates the base integer matrix and applies Latin Square rules and grid clues."""
    n = puzzle.n
    grid = [[model.NewIntVar(1, n, f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    for r in range(n):
        model.AddAllDifferent(grid[r])
        model.AddAllDifferent([grid[c][r] for c in range(n)])

    for r, c, val in puzzle.get_active_grid_given():
        model.Add(grid[r][c] == val)

    return grid


def _build_boolean_channeling(model: cp_model.CpModel, grid: List[List[cp_model.IntVar]], n: int) -> Tuple[List[List[Dict[int, cp_model.BoolVar]]], List[List[Dict[int, cp_model.BoolVar]]]]:
    """Generates the 3D boolean grids and channels them to the integer domains."""
    # Use dictionaries for the height dimension to strictly map 1 to n, avoiding unconstrained 0-index variables
    b_grid = [[{h: model.NewBoolVar(f"b_{r}_{c}_{h}") for h in range(1, n + 1)} for c in range(n)] for r in range(n)]
    ge_grid = [[{h: model.NewBoolVar(f"ge_{r}_{c}_{h}") for h in range(1, n + 1)} for c in range(n)] for r in range(n)]

    for r in range(n):
        for c in range(n):
            # Exactly one height must be true per cell
            model.AddExactlyOne([b_grid[r][c][h] for h in range(1, n + 1)])

            # The integer value equals the sum of the boolean index
            model.Add(grid[r][c] == sum([h * b_grid[r][c][h] for h in range(1, n + 1)]))

            # Define the 'Greater Than or Equal' binary flags for the shadows
            for h in range(1, n + 1):
                model.Add(sum([b_grid[r][c][k] for k in range(h, n + 1)]) == 1).OnlyEnforceIf(ge_grid[r][c][h])
                model.Add(sum([b_grid[r][c][k] for k in range(h, n + 1)]) == 0).OnlyEnforceIf(ge_grid[r][c][h].Not())

    return b_grid, ge_grid


def _apply_line_shadow_visibility(model: cp_model.CpModel, coords: List[Tuple[int, int]], clue: int, n: int,
                                  b_grid: List[List[Dict[int, cp_model.BoolVar]]], ge_grid: List[List[Dict[int, cp_model.BoolVar]]],
                                  direction: str, idx: int):
    """Encodes the Tseytin Prefix Shadow transformations and geometric constraints for a single line of sight."""
    vis_bits = [model.NewBoolVar(f"v_{direction}_{idx}_{i}") for i in range(n)]
    # Use dictionary for the height dimension here as well
    shadow = [{h: model.NewBoolVar(f"shadow_{direction}_{idx}_{i}_h{h}") for h in range(1, n + 1)} for i in range(n)]

    # Base Case: Step 0
    model.Add(vis_bits[0] == 1)
    r0, c0 = coords[0]
    for h in range(1, n + 1):
        model.Add(shadow[0][h] == ge_grid[r0][c0][h])

    # Recursive Chain
    for i in range(1, n):
        r_i, c_i = coords[i]

        for h in range(1, n + 1):
            # CP-SAT's AddMaxEquality on booleans acts exactly like logical OR
            model.AddMaxEquality(shadow[i][h], [shadow[i-1][h], ge_grid[r_i][c_i][h]])

        # A building is visible if its height is 'h', AND the shadow before it was NOT >= h
        and_terms = []
        for h in range(1, n + 1):
            term = model.NewBoolVar(f"term_{direction}_{idx}_{i}_{h}")
            model.AddBoolAnd([b_grid[r_i][c_i][h], shadow[i-1][h].Not()]).OnlyEnforceIf(term)
            model.AddBoolOr([b_grid[r_i][c_i][h].Not(), shadow[i-1][h]]).OnlyEnforceIf(term.Not())
            and_terms.append(term)

        # Since exactly one 'h' is active per cell, the sum works perfectly
        model.Add(vis_bits[i] == sum(and_terms))

    # Direct Target Clue Constraint
    model.Add(sum(vis_bits) == clue)

    # --- Generalization 1: Max-Shadow Rule ---
    for i in range(n - 1):
        for j in range(i + 1, n):
            model.Add(vis_bits[j] == 0).OnlyEnforceIf(shadow[i][n])

    # --- Generalization 2: Vision Capping Rule ---
    for i in range(n - 1):
        r, c = coords[i]
        for h in range(1, n + 1):
            remaining_slots = n - 1 - i
            max_remaining_vision = n - h
            if max_remaining_vision < remaining_slots:
                model.Add(sum(vis_bits[i+1:]) <= max_remaining_vision).OnlyEnforceIf(b_grid[r][c][h])


def _apply_all_visibility_clues(model: cp_model.CpModel, puzzle: Puzzle,
                                b_grid: List[List[List[cp_model.BoolVar]]], ge_grid: List[List[List[cp_model.BoolVar]]]):
    """Iterates through all puzzle perimeter definitions and applies the structural visibility constraints."""
    n = puzzle.n
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
                _apply_line_shadow_visibility(model, coords, k, n, b_grid, ge_grid, d, idx)


def create_base_solver(puzzle: Puzzle, randomize: bool = False):
    """Instantiates a Hybrid Boolean/Integer CP-SAT model using Tseytin Shadow Transformations."""
    model = cp_model.CpModel()

    # 1. Build the core Latin Square integer grid
    grid = _build_integer_grid(model, puzzle)

    # 2. Build the boolean grid and channel it to the integer logic
    b_grid, ge_grid = _build_boolean_channeling(model, grid, puzzle.n)

    # 3. Apply the structural prefix shadows
    _apply_all_visibility_clues(model, puzzle, b_grid, ge_grid)

    solver = cp_model.CpSolver()
    if randomize:
        import random
        solver.parameters.random_seed = random.randint(1, 1000000)

    return solver, model, grid
