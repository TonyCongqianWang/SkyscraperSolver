# core_engine.py
import sys
import random
from z3 import Solver, Int, And, Distinct, If, sat, Or, Not, Bool

def parse_puzzle(input_args):
    """Dynamically parses and maps incoming puzzle structures."""
    if isinstance(input_args, tuple) or (isinstance(input_args, list) and len(input_args) > 1):
        edge_str = input_args[0]
        grid_str = input_args[1] if len(input_args) > 1 else ""
        return parse_sequential_strings(edge_str, grid_str)

    src = input_args[0] if isinstance(input_args, list) else input_args
    src_stripped = src.strip()

    try:
        with open(src_stripped, 'r') as f:
            content = f.read().strip()
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return parse_sequential_strings(lines[0], lines[1] if len(lines) > 1 else "")
    except FileNotFoundError:
        return parse_sequential_strings(src_stripped, "")

def parse_sequential_strings(edge_str, grid_str):
    """Builds the puzzle structure from sequential space-separated parameter sequences."""
    edges = [int(x) for x in edge_str.split()]
    if not edges or len(edges) % 4 != 0:
        print(f"Error: Clue size ({len(edges)}) must be a non-zero multiple of 4.", file=sys.stderr)
        sys.exit(1)

    n = len(edges) // 4
    data = {
        "N": edges[0 : n], "S": edges[n : 2*n],
        "W": edges[2*n : 3*n], "E": edges[3*n : 4*n],
        "grid": [[0] * n for _ in range(n)]
    }

    if grid_str.strip():
        grid_flat = [int(x) for x in grid_str.split()]
        if len(grid_flat) != n * n:
            print(f"Error: Configuration requires {n*n} cells, got {len(grid_flat)}.", file=sys.stderr)
            sys.exit(1)
        data["grid"] = [grid_flat[i * n : (i + 1) * n] for i in range(n)]

    return n, data

def create_base_solver(n, puzzle_data, randomize=False):
    """Generates an optimized SMT translation map using pure boolean reduction arrays."""
    s = Solver()

    if randomize:
        s.set("random_seed", random.randint(1, 1000000))
        s.set("smt.random_seed", random.randint(1, 1000000))

    b_grid = [[[Bool(f"b_{r}_{c}_{h}") for h in range(n + 1)] for c in range(n)] for r in range(n)]
    grid = [[Int(f"cell_{r}_{c}") for c in range(n)] for r in range(n)]

    for r in range(n):
        s.add(Distinct(grid[r]))
        s.add(Distinct([grid[c][r] for c in range(n)]))
        for c in range(n):
            s.add(grid[r][c] >= 1, grid[r][c] <= n)

            for h in range(1, n + 1):
                s.add(b_grid[r][c][h] == (grid[r][c] == h))

            val = puzzle_data["grid"][r][c]
            if val > 0:
                s.add(grid[r][c] == val)

    def encode_visibility_boolean(line_coords, clue_val):
        if clue_val <= 0:
            return

        vis_flags = []
        vis_flags.append(1)

        for idx in range(1, n):
            curr_r, curr_c = line_coords[idx]

            cell_vis_conditions = []
            for h in range(1, n + 1):
                preceding_blocks = []
                for prev_idx in range(idx):
                    p_r, p_c = line_coords[prev_idx]
                    for k in range(h, n + 1):
                        preceding_blocks.append(b_grid[p_r][p_c][k])

                if preceding_blocks:
                    cell_vis_conditions.append(And(b_grid[curr_r][curr_c][h], Not(Or(preceding_blocks))))
                else:
                    cell_vis_conditions.append(b_grid[curr_r][curr_c][h])

            vis_flags.append(If(Or(cell_vis_conditions), 1, 0))

        s.add(sum(vis_flags) == clue_val)

    for idx in range(n):
        if puzzle_data["N"][idx] > 0:
            encode_visibility_boolean([(r, idx) for r in range(n)], puzzle_data["N"][idx])
        if puzzle_data["S"][idx] > 0:
            encode_visibility_boolean([(r, idx) for r in reversed(range(n))], puzzle_data["S"][idx])
        if puzzle_data["W"][idx] > 0:
            encode_visibility_boolean([(idx, c) for c in range(n)], puzzle_data["W"][idx])
        if puzzle_data["E"][idx] > 0:
            encode_visibility_boolean([(idx, c) for c in reversed(range(n))], puzzle_data["E"][idx])

    return s, grid

def serialize_puzzle_to_string(n, puzzle_data):
    """Converts a complete puzzle model into a standardized double-quoted parameter token sequence."""
    edge_parts = []
    for d in ["N", "S", "W", "E"]:
        edge_parts.extend(puzzle_data[d])
    edge_str = " ".join(str(x) for x in edge_parts)
    grid_str = " ".join(str(val) for row in puzzle_data["grid"] for val in row)
    return f'"{edge_str}" "{grid_str}"'

def serialize_matrix_to_string(grid_matrix):
    """Converts an internal matrix square into a space-separated string block."""
    return " ".join(str(val) for row in grid_matrix for val in row)

def render_ascii(n, grid_vals, clues=None):
    """Renders a layout cleanly tracking character alignments."""
    clues = clues or {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n}
    fmt = lambda v: str(v) if v > 0 else " "

    out = []
    out.append("   " + " ".join(fmt(x) for x in clues["N"]))
    out.append("  ┌" + "─" * (2 * n - 1) + "┐")
    for r in range(n):
        row_str = " ".join(str(grid_vals[r][c]) if grid_vals[r][c] > 0 else "." for c in range(n))
        out.append(f"{fmt(clues['W'][r])} │{row_str}│ {fmt(clues['E'][r])}")
    out.append("  └" + "─" * (2 * n - 1) + "┘")
    out.append("   " + " ".join(fmt(x) for x in clues["S"]))
    return "\n".join(out)

def render_grid_only(grid_vals):
    """Renders the core grid rows isolated without brackets, lines, or frame decorators."""
    return "\n".join(" ".join(str(x) for x in row) for row in grid_vals)

def has_unique_solution(n, puzzle_data):
    s, grid_vars = create_base_solver(n, puzzle_data, randomize=False)
    if s.check() != sat:
        return False
    m1 = s.model()
    s.add(Or([grid_vars[r][c] != m1[grid_vars[r][c]].as_long() for r in range(n) for c in range(n)]))
    return s.check() != sat
