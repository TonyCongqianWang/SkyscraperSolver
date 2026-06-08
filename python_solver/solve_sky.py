import sys
import argparse
import shlex
from parser import parse_puzzle_input
from renderer import render_grid_flat, render_ascii_frame, serialize_to_string
from ortools.sat.python import cp_model

class SkyscraperSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Unified native callback hook that accumulates solutions up to an arbitrary limit."""
    def __init__(self, grid_vars, limit=0):
        super().__init__()
        self._grid_vars = grid_vars
        self._limit = limit
        self.solutions = []

    def on_solution_callback(self):
        n = len(self._grid_vars)
        sol = [[self.value(self._grid_vars[r][c]) for c in range(n)] for r in range(n)]
        self.solutions.append(sol)

        # Force immediate termination of the C++ loop if the threshold limit is met
        if self._limit > 0 and len(self.solutions) >= self._limit:
            self.stop_search()

def solve_and_output(p, args, puzzle_id="", f=sys.stdout):
    found = 0
    buffer = []

    # --- Z3 BACKEND (Direct Constraints) ---
    if args.backend == "z3":
        from solver_core_z3 import create_base_solver
        from z3 import sat, Or

        solver, grid_vars = create_base_solver(p, randomize=True)

        while True:
            if solver.check() != sat:
                break
            found += 1
            m = solver.model()
            sol = [[m[grid_vars[r][c]].as_long() for c in range(p.n)] for r in range(p.n)]

            if args.num_solutions != 0:
                if args.print_format == "grid":
                    buffer.append(render_grid_flat(sol))
                elif args.print_format == "string":
                    buffer.append(serialize_to_string(p, sol))
                elif args.print_format == "all":
                    buffer.append(f"--- Solution #{found} ---\n{render_ascii_frame(p.n, sol, p.clues)}\n{serialize_to_string(p, sol)}")

            solver.add(Or([grid_vars[r][c] != sol[r][c] for r in range(p.n) for c in range(p.n)]))
            if args.num_solutions > 0 and found >= args.num_solutions:
                break

    # --- CP-SAT BACKEND (Unified Native Callback) ---
    elif args.backend == "cpsat":
        from solver_core_cpsat import create_base_solver as create_cp_solver

        # 1. Initialize the C++ model definitions
        solver, model, grid_vars = create_cp_solver(p, randomize=True)

        # 2. Spin up the solution tracker bound directly to your CLI limit argument
        solution_printer = SkyscraperSolutionPrinter(grid_vars, limit=args.num_solutions)

        # 3. Enable the native multi-solution state preservation flag
        solver.parameters.enumerate_all_solutions = True

        # 4. Run the single-pass solve action natively (ignores volatile return status)
        solver.Solve(model, solution_printer)

        # 5. Extract and format the accumulated solutions cleanly from the callback object
        for sol in solution_printer.solutions:
            found += 1
            prefix = f"{puzzle_id} " if puzzle_id else ""
            if args.num_solutions != 0:
                if args.print_format == "grid":
                    buffer.append(f"{prefix}{render_grid_flat(sol)}")
                elif args.print_format == "string":
                    buffer.append(f"{prefix}{serialize_to_string(p, sol)}")
                elif args.print_format == "all":
                    buffer.append(f"--- Solution #{found} {prefix}---\n{render_ascii_frame(p.n, sol, p.clues)}\n{serialize_to_string(p, sol)}")

    # Handle unsatisfiable fallbacks cleanly based on actual extracted solution count
    if found == 0:
        prefix = f"{puzzle_id} " if puzzle_id else ""
        buffer.append(f"{prefix}UNSATISFIABLE (No Solution Found)")

    if args.print_format == "all" and found > 0:
        print(f"Total Unique Solutions Found: {found}\n", file=f)

    # Flush the text arrays down the designated IO stream completely
    for solution in buffer:
        print(solution, file=f)

    print("--- END_OF_INSTANCE ---", file=f)
    if f == sys.stdout:
        sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Skyscraper Puzzle Solver Engine.")
    parser.add_argument("input", type=str, nargs="*", help="Input properties (Optional. If omitted, reads from stdin).")
    parser.add_argument("-b", "--backend", type=str, choices=["z3", "cpsat"], default="cpsat", help="Solver backend to use.")
    parser.add_argument("-s", "--num_solutions", type=int, default=1, help="Max solutions to track.")
    parser.add_argument("-p", "--print_format", type=str, choices=["grid", "string", "all"], default="all")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output destination file path.")
    args = parser.parse_args()

    f = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout

    if args.input:
        p = parse_puzzle_input(args.input)
        solve_and_output(p, args, f=f)
    else:
        for line_no, line in enumerate(sys.stdin, 1):
            line = line.strip()
            if not line: continue
            try:
                parsed_args = shlex.split(line)
                p = parse_puzzle_input(parsed_args)
                solve_and_output(p, args, puzzle_id=f"[Line {line_no}]", f=f)
            except Exception as e:
                print(f"Error processing line {line_no}: {e}", file=sys.stderr)
                print("--- END_OF_INSTANCE ---", file=f)
                if f == sys.stdout: sys.stdout.flush()

    if args.output:
        f.close()

if __name__ == "__main__":
    main()
