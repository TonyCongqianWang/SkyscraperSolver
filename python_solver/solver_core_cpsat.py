import itertools
from typing import Tuple, List
from ortools.sat.python import cp_model
from models import Puzzle

from ortools.sat.python import cp_model


class SkyscraperSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Unified native callback hook that accumulates solutions up to an arbitrary limit."""
    def __init__(self, grid_vars, limit=0):
        super().__init__()
        self._grid_vars = grid_vars
        self._limit = limit
        self.solutions = []

    def on_solution_callback(self):
        n = len(self._grid_vars)
        sol = [[self.value(self._grid_vars[r][c]) for c in range(n)] for r in range(n)]
        self.solutions.append(sol)

        # If an explicit non-zero limit is set, halt the C++ engine immediately upon hit
        if self._limit > 0 and len(self.solutions) >= self._limit:
            self.stop_search()


# In-Memory Cache (Persists for the lifespan of the batch script)
_TUPLE_CACHE = {}

def get_valid_tuples(n: int, clue_start: int, clue_end: int) -> List[Tuple]:
    """Generates or retrieves all mathematically valid permutations for a row."""
    cache_key = (n, clue_start, clue_end)
    if cache_key in _TUPLE_CACHE:
        return _TUPLE_CACHE[cache_key]

    valid_tuples = []
    for p in itertools.permutations(range(1, n + 1)):
        if clue_start > 0:
            vis = 0
            m = 0
            for val in p:
                if val > m:
                    vis += 1
                    m = val
                    if m == n: break
            if vis != clue_start:
                continue

        if clue_end > 0:
            vis = 0
            m = 0
            for val in reversed(p):
                if val > m:
                    vis += 1
                    m = val
                    if m == n: break
            if vis != clue_end:
                continue

        valid_tuples.append(p)

    _TUPLE_CACHE[cache_key] = valid_tuples
    return valid_tuples

def create_base_solver(puzzle: Puzzle, randomize: bool = False):
    """Instantiates a highly constrained CP-SAT model using Table Constraints."""
    model = cp_model.CpModel()
    n = puzzle.n
    grid = [[model.NewIntVar(1, n, f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    for r in range(n):
        model.AddAllDifferent(grid[r])
        model.AddAllDifferent([grid[c][r] for c in range(n)])

    for r, c, val in puzzle.get_active_grid_given():
        model.Add(grid[r][c] == val)

    # Apply Extensional Constraints (Tables)
    for r in range(n):
        clue_w = puzzle.clues["W"][r]
        clue_e = puzzle.clues["E"][r]
        if clue_w > 0 or clue_e > 0:
            valid_tuples = get_valid_tuples(n, clue_w, clue_e)
            model.AddAllowedAssignments(grid[r], valid_tuples)

    for c in range(n):
        clue_n = puzzle.clues["N"][c]
        clue_s = puzzle.clues["S"][c]
        if clue_n > 0 or clue_s > 0:
            valid_tuples = get_valid_tuples(n, clue_n, clue_s)
            col_vars = [grid[r][c] for r in range(n)]
            model.AddAllowedAssignments(col_vars, valid_tuples)

    solver = cp_model.CpSolver()
    if randomize:
        import random
        solver.parameters.random_seed = random.randint(1, 1000000)

    return solver, model, grid
