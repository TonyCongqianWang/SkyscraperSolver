import sys
import argparse
import shlex
from parser import parse_puzzle_input
from renderer import render_grid_flat, render_ascii_frame, serialize_to_string

# Persistent global registers to preserve Z3 incremental clause sharing for -s 1
_Z3_SOLVER = None
_Z3_VARS = None
_Z3_LITERALS = None
_Z3_CURRENT_N = None

def solve_and_output(p, args, puzzle_id="", f=sys.stdout):
    global _Z3_SOLVER, _Z3_VARS, _Z3_LITERALS, _Z3_CURRENT_N
    found = 0
    buffer = []
    prefix = f"{puzzle_id} " if puzzle_id else ""

    # --- Z3 BACKEND ---
    if args.backend == "z3":
        from z3 import sat, Or

        if 0 < args.num_solutions < 20:
            # --- STRATEGY A: Dynamic Incremental Core (Batch Solution Enumeration Track) ---
            from solver_core_z3 import create_base_solver_with_assumptions, add_puzzle_clues_to_assumptions

            if _Z3_CURRENT_N != p.n:
                _Z3_CURRENT_N = p.n
                _Z3_SOLVER, _Z3_VARS, _Z3_LITERALS = create_base_solver_with_assumptions(p)
            else:
                # Add any missing value-specific constraints dynamically to the shared workspace
                add_puzzle_clues_to_assumptions(_Z3_SOLVER, _Z3_VARS, p, _Z3_LITERALS)

            # Map inputs to the exact value-specific literal flags
            instance_assumptions = []
            for d, idx, val in p.get_active_clues():
                instance_assumptions.append(_Z3_LITERALS[("edge", d, idx, val)] == True)
            for r, c, val in p.get_active_grid_given():
                instance_assumptions.append(_Z3_LITERALS[("grid", r, c, val)] == True)

            _Z3_SOLVER.push()

            # Continuous check loop under active assumptions
            while True:
                if _Z3_SOLVER.check(*instance_assumptions) != sat:
                    break

                found += 1
                m = _Z3_SOLVER.model()
                sol = [[m[_Z3_VARS[r][c]].as_long() for c in range(p.n)] for r in range(p.n)]

                if args.print_format == "grid":
                    buffer.append(f"{prefix}{render_grid_flat(sol)}\n\n")
                elif args.print_format == "string":
                    buffer.append(f"{prefix}{serialize_to_string(p, sol)}\n\n")
                elif args.print_format == "all":
                    buffer.append(f"--- Solution #{found} {prefix}---\n\n{render_ascii_frame(p.n, sol, p.clues)}\n{serialize_to_string(p, sol)}\n\n")

                # Block the exact grid combination from being found again in this sub-frame
                _Z3_SOLVER.add(Or([_Z3_VARS[r][c] != sol[r][c] for r in range(p.n) for c in range(p.n)]))

                # Halt if we hit the user-specified threshold
                if found >= args.num_solutions:
                    break

            _Z3_SOLVER.pop()

        else:
            # --- STRATEGY B: Standalone Sandbox Core (Pure Independent -s 0 Exploration Track) ---
            from solver_core_z3 import create_base_solver
            solver, grid_vars = create_base_solver(p, randomize=True)

            while True:
                if solver.check() != sat:
                    break
                found += 1
                m = solver.model()
                sol = [[m[grid_vars[r][c]].as_long() for c in range(p.n)] for r in range(p.n)]

                if args.num_solutions != 0:
                    if args.print_format == "grid":
                        buffer.append(f"{prefix}{render_grid_flat(sol)}\n\n")
                    elif args.print_format == "string":
                        buffer.append(f"{prefix}{serialize_to_string(p, sol)}\n\n")
                    elif args.print_format == "all":
                        buffer.append(f"--- Solution #{found} {prefix}---\n\n{render_ascii_frame(p.n, sol, p.clues)}\n{serialize_to_string(p, sol)}\n\n")

                solver.add(Or([grid_vars[r][c] != sol[r][c] for r in range(p.n) for c in range(p.n)]))
                if args.num_solutions > 0 and found >= args.num_solutions:
                    break

    # --- CP-SAT BACKEND (Using native callback arrays) ---
    elif args.backend == "cpsat":
        from solver_core_cpsat import create_base_solver, SkyscraperSolutionPrinter

        solver, model, grid_vars = create_base_solver(p, randomize=True)
        solution_printer = SkyscraperSolutionPrinter(grid_vars, limit=args.num_solutions)
        solver.parameters.enumerate_all_solutions = True
        solver.Solve(model, solution_printer)

        for sol in solution_printer.solutions:
            found += 1
            if args.num_solutions != 0:
                if args.print_format == "grid":
                    buffer.append(f"{prefix}{render_grid_flat(sol)}\n\n")
                elif args.print_format == "string":
                    buffer.append(f"{prefix}{serialize_to_string(p, sol)}\n\n")
                elif args.print_format == "all":
                    buffer.append(f"--- Solution #{found} {prefix}---\n\n{render_ascii_frame(p.n, sol, p.clues)}\n{serialize_to_string(p, sol)}\n\n")

    if found == 0:
        buffer.append(f"{prefix}UNSATISFIABLE (No Solution Found)")

    if args.print_format == "all" and found > 0:
        print(f"Total Unique Solutions Found: {found}\n", file=f)

    for solution in buffer:
        print(solution, file=f)

    print("--- END_OF_INSTANCE ---", file=f)
    if f == sys.stdout:
        sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Skyscraper Puzzle Solver Engine.")
    parser.add_argument("input", type=str, nargs="*", help="Input properties (optional if --stdin is used).")
    parser.add_argument("-b", "--backend", type=str, choices=["z3", "cpsat"], default=None, help="Solver backend to use.")
    parser.add_argument("-s", "--num_solutions", type=int, default=1, help="Max solutions to track.")
    parser.add_argument("-p", "--print_format", type=str, choices=["grid", "string", "all"], default="all")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output destination file path.")
    parser.add_argument("--stdin", action="store_true", help="Read puzzles sequentially from stdin.")
    args = parser.parse_args()

    if args.backend is None:
        args.backend = "z3" if args.num_solutions == 1 else "cpsat"
        print(f"Auto-selected backend: {args.backend}", file=sys.stdout)

    f = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout

    if args.stdin:
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
    elif args.input:
        p = parse_puzzle_input(args.input)
        solve_and_output(p, args, f=f)
    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        f.close()

if __name__ == "__main__":
    main()
