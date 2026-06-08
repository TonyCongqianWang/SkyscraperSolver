from typing import List, Dict

class Puzzle:
    def __init__(self, n: int, clues: Dict[str, List[int]], initial_grid: List[List[int]]):
        self.n = n
        self.clues = clues  # Keys: 'N', 'S', 'W', 'E'
        self.grid = initial_grid

    def get_active_clues(self):
        """Yields (direction, index, value) for all non-zero edge clues."""
        for d in ["N", "S", "W", "E"]:
            for idx in range(self.n):
                val = self.clues[d][idx]
                if val > 0:
                    yield (d, idx, val)

    def get_active_grid_given(self):
        """Yields (row, col, value) for all non-zero given cells."""
        for r in range(self.n):
            for c in range(self.n):
                val = self.grid[r][c]
                if val > 0:
                    yield (r, c, val)
