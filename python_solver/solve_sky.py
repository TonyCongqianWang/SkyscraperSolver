# solve_sky.py
import argparse
from z3 import sat, Or
from core_engine import (parse_puzzle, create_base_solver, render_ascii,
                         render_grid_only, serialize_puzzle_to_string)

def main():
    parser = argparse.ArgumentParser(description="Skyscraper Puzzle SMT Solver Engine.")
    parser.add_argument("input", type=str, nargs="+", help="Accepts space strings, text file targets, or tokens.")
    parser.add_argument("-n", "--num_solutions", type=int, default=1, help="Total solutions to track. Set 0 to count execution totals.")
    parser.add_argument("-p", "--print_format", type=str, choices=["grid", "string", "all"], default="all",
                        help="Formatting type options for puzzle solution rendering profiles.")
    parser.add_argument("-o", "--output", type=str, default=None, help="Target location destination text file path.")
    args = parser.parse_args()

    n, puzzle_data = parse_puzzle(args.input)
    solver, grid_vars = create_base_solver(n, puzzle_data, randomize=True)

    solutions_found = 0
    results_buffer = []

    while True:
        if solver.check() == sat:
            solutions_found += 1
            model = solver.model()
            curr_solution = [[model[grid_vars[r][c]].as_long() for c in range(n)] for r in range(n)]

            # Synthesize solution back into original format schema
            solution_data = {
                "N": puzzle_data["N"], "S": puzzle_data["S"],
                "W": puzzle_data["W"], "E": puzzle_data["E"],
                "grid": curr_solution
            }
            solution_string = serialize_puzzle_to_string(n, solution_data)

            if args.num_solutions != 0:
                formatted_parts = []

                if args.print_format == "grid":
                    formatted_parts.append(render_grid_only(curr_solution))
                elif args.print_format == "string":
                    formatted_parts.append(solution_string)
                elif args.print_format == "all":
                    viz_layer = f"--- Solution #{solutions_found} ---\n" + render_ascii(n, curr_solution, puzzle_data)
                    formatted_parts.append(f"{viz_layer}\n{solution_string}")

                results_buffer.append("\n".join(formatted_parts))

            solver.add(Or([grid_vars[r][c] != curr_solution[r][c] for r in range(n) for c in range(n)]))
            if args.num_solutions > 0 and solutions_found >= args.num_solutions:
                break
        else:
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
