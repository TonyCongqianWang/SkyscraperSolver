import argparse
from models import Puzzle
from generator import generate_random_latin_square, compute_all_clues, minimize_puzzle
from renderer import render_ascii_frame, serialize_to_string

def main():
    parser = argparse.ArgumentParser(description="Minimal Skyscraper Generator Engine.")
    parser.add_argument("-s", "--size", type=int, default=4, help="Grid dimension size boundary integer n.")
    parser.add_argument("--allow-grid-clues", action="store_true", help="Allow clues to remain inside internal cells.")
    args = parser.parse_args()

    n = args.size
    solution_grid = generate_random_latin_square(n)
    full_clues = compute_all_clues(n, solution_grid)
    min_puzzle = minimize_puzzle(n, full_clues, solution_grid, args.allow_grid_clues)

    solution_puzzle = Puzzle(n, min_puzzle.clues, solution_grid)

    print("=== GENERATED PUZZLE ===")
    print(render_ascii_frame(n, min_puzzle.grid, min_puzzle.clues))
    print(f"STRING FORMAT:\n{serialize_to_string(min_puzzle, min_puzzle.grid)}")

    print("\n=== EXPECTED UNIQUE SOLUTION ===")
    print(render_ascii_frame(n, solution_grid, min_puzzle.clues))
    print(f"STRING FORMAT:\n{serialize_to_string(solution_puzzle, solution_grid)}")

if __name__ == "__main__":
    main()
