from typing import List, Dict, Optional
from models import Puzzle, SolutionGrid

def serialize_to_string(puzzle: Puzzle, matrix: List[List[int]]) -> str:
    """Converts a complete runtime data state into dual token sequences."""
    edge_parts = []
    for direction in ["N", "S", "W", "E"]:
        edge_parts.extend(puzzle.clues[direction])

    edge_str = " ".join(str(x) for x in edge_parts)
    grid_str = " ".join(str(val) for row in matrix for val in row)
    return f'"{edge_str}" "{grid_str}"'

def render_grid_flat(matrix: List[List[int]]) -> str:
    """Isolates the raw grid output blocks completely clear of lines."""
    return "\n".join(" ".join(str(x) for x in row) for row in matrix)

def render_ascii_frame(n: int, matrix: List[List[int]], clues: Optional[Dict[str, List[int]]] = None) -> str:
    """Renders formatted matrix views bound inside explicit visual borders."""
    clues = clues or {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n}
    fmt = lambda v: str(v) if v > 0 else " "

    out = []
    out.append("   " + " ".join(fmt(x) for x in clues["N"]))
    out.append("  ┌" + "─" * (2 * n - 1) + "┐")
    for r in range(n):
        row_str = " ".join(str(matrix[r][c]) if matrix[r][c] > 0 else "." for c in range(n))
        out.append(f"{fmt(clues['W'][r])} │{row_str}│ {fmt(clues['E'][r])}")
    out.append("  └" + "─" * (2 * n - 1) + "┘")
    out.append("   " + " ".join(fmt(x) for x in clues["S"]))
    return "\n".join(out)
