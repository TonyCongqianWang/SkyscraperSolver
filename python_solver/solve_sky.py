import argparse
from z3 import sat, Or
from parser import parse_puzzle_input
from solver_core import create_base_solver
from renderer import render_grid_flat, render_ascii_frame, serialize_to_string

def main():
    parser = argparse.ArgumentParser(description="Skyscraper Puzzle SMT Solver Engine.")
    parser.add_argument("input", type=str, nargs="+", help="Accepts space strings, text file targets, or tokens.")
    parser.add_argument("-n", "--num_solutions", type=int, default=1, help="Total solutions to track.")
    parser.add_argument("-p", "--print_format", type=str, choices=["grid", "string", "all"], default="all")
    parser.add_argument("-o", "--output", type=str, default=None, help="Target file destination destination path.")
    args = parser.parse_args()

    puzzle = parse_puzzle_input(args.input)
    solver, grid_vars = create_base_solver(puzzle, randomize=True)

    solutions_found = 0
    results_buffer = []

    while True:
        if solver.check() != sat:
            break

        solutions_found += 1
        model = solver.model()
        curr_solution = [[model[grid_vars[r][c]].as_long() for c in range(puzzle.n)] for r in range(puzzle.n)]

        if args.num_solutions != 0:
            formatted_parts = []
            if args.print_format == "grid":
                formatted_parts.append(render_grid_flat(curr_solution))
            elif args.print_format == "string":
                formatted_parts.append(serialize_to_string(puzzle, curr_solution))
            elif args.print_format == "all":
                viz = f"--- Solution #{solutions_found} ---\n" + render_ascii_frame(puzzle.n, curr_solution, puzzle.clues)
                formatted_parts.append(f"{viz}\n{serialize_to_string(puzzle, curr_solution)}")

            results_buffer.append("\n".join(formatted_parts))

        # Add tracking rule blocking current exact combination matrix setup
        solver.add(Or([grid_vars[r][c] != curr_solution[r][c] for r in range(puzzle.n) for c in range(puzzle.n)]))
        if args.num_solutions > 0 and solutions_found >= args.num_solutions:
            break

    output_text = f"Total Unique Solutions Found: {solutions_found}\n" if args.num_solutions == 0 else (
        "\n\n".join(results_buffer) if results_buffer else "No valid configurations found matching constraints (UNSAT)."
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text + "\n")
        print(f"Execution successfully written out to: {args.output}")
    else:
        print(output_text)

if __name__ == "__main__":
    main()
