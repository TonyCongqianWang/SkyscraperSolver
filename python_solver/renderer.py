from typing import List, Dict, Optional
from models import Puzzle

def serialize_to_string(puzzle: Puzzle, matrix: List[List[int]]) -> str:
    edge_parts = []
    for direction in ["N", "S", "W", "E"]:
        edge_parts.extend(puzzle.clues[direction])
    return f'"{" ".join(str(x) for x in edge_parts)}" "{" ".join(str(v) for r in matrix for v in r)}"'

def render_grid_flat(matrix: List[List[int]]) -> str:
    return "\n".join(" ".join(str(x) for x in row) for row in matrix)

def render_ascii_frame(n: int, matrix: List[List[int]], clues: Optional[Dict[str, List[int]]] = None) -> str:
    clues = clues or {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n}
    fmt = lambda v: str(v) if v > 0 else " "
    out = ["   " + " ".join(fmt(x) for x in clues["N"]), "  ┌" + "─" * (2 * n - 1) + "┐"]
    for r in range(n):
        row_str = " ".join(str(matrix[r][c]) if matrix[r][c] > 0 else "." for c in range(n))
        out.append(f"{fmt(clues['W'][r])} │{row_str}│ {fmt(clues['E'][r])}")
    out.append("  └" + "─" * (2 * n - 1) + "┘")
    out.append("   " + " ".join(fmt(x) for x in clues["S"]))
    return "\n".join(out)
