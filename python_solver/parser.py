import os
import sys
from typing import List
from models import Puzzle

class PuzzleParseError(ValueError):
    """Custom exception raised for puzzle parsing errors."""
    pass

def parse_puzzle_input(input_args: List[str]) -> Puzzle:
    """Parses raw text, cli arguments, or file paths into a structured Puzzle instance."""
    if not input_args:
        raise PuzzleParseError("No input arguments provided.")

    if len(input_args) > 1 or isinstance(input_args, tuple):
        return _from_sequences(str(input_args[0]), str(input_args[1]) if len(input_args) > 1 else "")

    src = input_args[0].strip()
    if os.path.isfile(src):
        try:
            with open(src, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            raise PuzzleParseError(f"Failed to read file '{src}': {e}")
        if not lines:
            raise PuzzleParseError(f"Puzzle file '{src}' is empty.")
        return _from_sequences(lines[0], lines[1] if len(lines) > 1 else "")

    return _from_sequences(src, "")

def _from_sequences(edge_str: str, grid_str: str) -> Puzzle:
    try:
        edges = [int(x) for x in edge_str.split()]
    except ValueError as e:
        raise PuzzleParseError(f"Invalid integer format in clues: {e}")

    if not edges or len(edges) % 4 != 0:
        raise PuzzleParseError(f"Clue size ({len(edges)}) must be a non-zero multiple of 4.")

    n = len(edges) // 4
    clues = {"N": edges[0:n], "S": edges[n:2*n], "W": edges[2*n:3*n], "E": edges[3*n:4*n]}
    grid = [[0] * n for _ in range(n)]

    if grid_str.strip():
        try:
            grid_flat = [int(x) for x in grid_str.split()]
        except ValueError as e:
            raise PuzzleParseError(f"Invalid integer format in grid: {e}")
        if len(grid_flat) != n * n:
            raise PuzzleParseError(f"Configuration requires {n*n} cells, got {len(grid_flat)}.")
        grid = [grid_flat[i * n : (i + 1) * n] for i in range(n)]

    return Puzzle(n, clues, grid)
