from typing import List, Dict

class Puzzle:
    def __init__(self, n: int, clues: Dict[str, List[int]], initial_grid: List[List[int]]):
        self.n = n
        self.clues = clues  # Expects keys: 'N', 'S', 'W', 'E'
        self.grid = initial_grid

class SolutionGrid:
    def __init__(self, n: int, matrix: List[List[int]]):
        self.n = n
        self.matrix = matrix
