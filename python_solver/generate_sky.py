import argparse
import sys
from models import Puzzle
from generator import generate_random_latin_square, compute_all_clues, minimize_puzzle
from renderer import render_ascii_frame, serialize_to_string

def main():
    parser = argparse.ArgumentParser(description="Minimal Skyscraper Generator Engine.")
    parser.add_argument("-s", "--size", type=int, default=4, help="Grid size.")
    parser.add_argument("--allow-grid-clues", action="store_true", help="Allow internal cell clues.")
    args = parser.parse_args()

    n = args.size
    sol = generate_random_latin_square(n)
    clues = compute_all_clues(n, sol)
    min_p, is_unique = minimize_puzzle(n, clues, sol, args.allow_grid_clues)

    if not is_unique:
        print("┌────────────────────────────────────────────────────────────────────────┐", file=sys.stderr)
        print("│ WARNING: Puzzle is NOT unique under current structural bounds!         │", file=sys.stderr)
        print("│ Higher grid dimensions typically require internal clues to hold unity. │", file=sys.stderr)
        print("└────────────────────────────────────────────────────────────────────────┘", file=sys.stderr)

    print("=== GENERATED PUZZLE ===")
    print(render_ascii_frame(n, min_p.grid, min_p.clues))
    print(f"STRING FORMAT:\n{serialize_to_string(min_p, min_p.grid)}")

    print("\n=== EXPECTED SOLUTION ===")
    print(render_ascii_frame(n, sol, min_p.clues))
    print(f"STRING FORMAT:\n{serialize_to_string(Puzzle(n, min_p.clues, sol), sol)}")

if __name__ == "__main__":
    main()
