import os
import sys
from typing import List, Tuple, Dict
from models import Puzzle

def parse_puzzle_input(input_args: List[str]) -> Puzzle:
    """Parses entry point strings, lists, or file targets into a Puzzle instance."""
    if len(input_args) > 1 or isinstance(input_args, tuple):
        return _from_sequences(str(input_args[0]), str(input_args[1]) if len(input_args) > 1 else "")

    src = input_args[0].strip()
    if os.path.isfile(src):
        with open(src, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        return _from_sequences(lines[0], lines[1] if len(lines) > 1 else "")

    return _from_sequences(src, "")

def _from_sequences(edge_str: str, grid_str: str) -> Puzzle:
    """Builds structured puzzle instances from sequential space-separated tokens."""
    edges = [int(x) for x in edge_str.split()]
    if not edges or len(edges) % 4 != 0:
        print(f"Error: Clue size ({len(edges)}) must be a non-zero multiple of 4.", file=sys.stderr)
        sys.exit(1)

    n = len(edges) // 4
    clues = {
        "N": edges[0 : n],
        "S": edges[n : 2*n],
        "W": edges[2*n : 3*n],
        "E": edges[3*n : 4*n]
    }

    grid = [[0] * n for _ in range(n)]
    if grid_str.strip():
        grid_flat = [int(x) for x in grid_str.split()]
        if len(grid_flat) != n * n:
            print(f"Error: Configuration requires {n*n} cells, got {len(grid_flat)}.", file=sys.stderr)
            sys.exit(1)
        grid = [grid_flat[i * n : (i + 1) * n] for i in range(n)]

    return Puzzle(n, clues, grid)
