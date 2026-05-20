# generate_sky.py
import argparse
import random
from z3 import Solver, sat
from core_engine import create_base_solver, has_unique_solution, render_ascii, serialize_puzzle_to_string

def generate_random_latin_square(n):
    blank_data = {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n, "grid": [[0]*n for _ in range(n)]}
    solver, grid_vars = create_base_solver(n, blank_data, randomize=True)

    cells = [(r, c) for r in range(n) for c in range(n)]
    random.shuffle(cells)

    for r, c in cells:
        s_tmp = Solver()
        s_tmp.add(solver.assertions())
        if s_tmp.check() == sat:
            val = s_tmp.model()[grid_vars[r][c]].as_long()
            solver.push()
            solver.add(grid_vars[r][c] == val)
            if solver.check() != sat:
                solver.pop()
        else:
            break

    if solver.check() == sat:
        return [[solver.model()[grid_vars[r][c]].as_long() for c in range(n)] for r in range(n)]
    raise RuntimeError("Base initialization array split.")

def compute_all_clues(n, solution_grid):
    clues = {"N": [0]*n, "S": [0]*n, "E": [0]*n, "W": [0]*n}
    def count_line(line):
        highest, visible = 0, 0
        for item in line:
            if item > highest:
                visible += 1
                highest = item
        return visible

    for i in range(n):
        clues["N"][i] = count_line([solution_grid[r][i] for r in range(n)])
        clues["S"][i] = count_line([solution_grid[r][i] for r in reversed(range(n))])
        clues["W"][i] = count_line([solution_grid[i][c] for c in range(n)])
        clues["E"][i] = count_line([solution_grid[i][c] for c in reversed(range(n))])
    return clues

def minimize_puzzle(n, full_clues, solution_grid, allow_grid_clues=False):
    puzzle = {
        "N": list(full_clues["N"]), "S": list(full_clues["S"]),
        "W": list(full_clues["W"]), "E": list(full_clues["E"]),
        "grid": [[0]*n for _ in range(n)]
    }

    clue_pool = [("edge", d, idx) for d in ["N", "S", "W", "E"] for idx in range(n)]
    if allow_grid_clues:
        puzzle["grid"] = [list(row) for row in solution_grid]
        clue_pool.extend([("grid", r, c) for r in range(n) for c in range(n)])

    random.shuffle(clue_pool)

    for item in clue_pool:
        if item[0] == "edge":
            _, direction, idx = item
            saved_val = puzzle[direction][idx]
            puzzle[direction][idx] = 0
            if not has_unique_solution(n, puzzle):
                puzzle[direction][idx] = saved_val
        else:
            _, r, c = item
            saved_val = puzzle["grid"][r][c]
            puzzle["grid"][r][c] = 0
            if not has_unique_solution(n, puzzle):
                puzzle["grid"][r][c] = saved_val

    return puzzle

def main():
    parser = argparse.ArgumentParser(description="Minimal Skyscraper Generator Engine.")
    parser.add_argument("-s", "--size", type=int, default=4, help="Grid dimension size boundary integer n.")
    parser.add_argument("--allow-grid-clues", action="store_true", help="Allow clues to remain inside internal cells.")
    args = parser.parse_args()

    n = args.size
    solution_grid = generate_random_latin_square(n)
    full_clues = compute_all_clues(n, solution_grid)
    min_puzzle = minimize_puzzle(n, full_clues, solution_grid, args.allow_grid_clues)

    # Pack solved data state matrix properties for uniform serialization prints
    solution_puzzle_data = {
        "N": min_puzzle["N"], "S": min_puzzle["S"],
        "W": min_puzzle["W"], "E": min_puzzle["E"],
        "grid": solution_grid
    }

    print("=== GENERATED PUZZLE ===")
    print(render_ascii(n, min_puzzle["grid"], min_puzzle))
    print(f"STRING FORMAT:\n{serialize_puzzle_to_string(n, min_puzzle)}")

    print("\n=== EXPECTED UNIQUE SOLUTION ===")
    print(render_ascii(n, solution_grid, min_puzzle))
    print(f"STRING FORMAT:\n{serialize_puzzle_to_string(n, solution_puzzle_data)}")

if __name__ == "__main__":
    main()
