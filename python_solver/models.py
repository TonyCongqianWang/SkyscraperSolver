from typing import List, Dict

class Puzzle:
    def __init__(self, n: int, clues: Dict[str, List[int]], initial_grid: List[List[int]]):
        self.n = n
        self.clues = clues  # Keys: 'N', 'S', 'W', 'E'
        self.grid = initial_grid
