import sys
import argparse
import shlex
from parser import parse_puzzle_input
from renderer import render_grid_flat, render_ascii_frame, serialize_to_string

_Z3_SOLVER = None
_Z3_VARS = None
_Z3_LITERALS = None
_Z3_CURRENT_N = None

def solve_and_output(p, args, puzzle_id="", f=sys.stdout):
    global _Z3_SOLVER, _Z3_VARS, _Z3_LITERALS, _Z3_CURRENT_N

    found = 0
    buffer = []

    if args.backend == "z3":
        from solver_core_z3 import create_base_solver_with_assumptions
        from z3 import sat, Or

        if _Z3_CURRENT_N != p.n:
            _Z3_CURRENT_N = p.n
            _Z3_SOLVER, _Z3_VARS, _Z3_LITERALS = create_base_solver_with_assumptions(p.n)

        assumptions = []
        for d, idx, val in p.get_active_clues():
            assumptions.append(_Z3_LITERALS[("edge", d, idx, val)] == True)
        for r, c, val in p.get_active_grid_given():
            assumptions.append(_Z3_LITERALS[("grid", r, c, val)] == True)

        _Z3_SOLVER.push()

        while True:
            if _Z3_SOLVER.check(*assumptions) != sat:
                break
            m = _Z3_SOLVER.model()
            sol = [[m[_Z3_VARS[r][c]].as_long() for c in range(p.n)] for r in range(p.n)]
            found += 1

            prefix = f"{puzzle_id} " if puzzle_id else ""
            if args.num_solutions != 0:
                if args.print_format == "grid":
                    buffer.append(f"{prefix}{render_grid_flat(sol)}")
                elif args.print_format == "string":
                    buffer.append(f"{prefix}{serialize_to_string(p, sol)}")
                elif args.print_format == "all":
                    buffer.append(f"--- Solution #{found} {prefix}---\n{render_ascii_frame(p.n, sol, p.clues)}\n{serialize_to_string(p, sol)}")

            if args.num_solutions > 0 and found >= args.num_solutions:
                break
            _Z3_SOLVER.add(Or([_Z3_VARS[r][c] != sol[r][c] for r in range(p.n) for c in range(p.n)]))

        _Z3_SOLVER.pop()

    elif args.backend == "cpsat":
        from solver_core_cpsat import create_base_solver
        from ortools.sat.python import cp_model

        solver, model, grid_vars = create_base_solver(p, randomize=True)

        while True:
            status = solver.Solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                break
            sol = [[solver.Value(grid_vars[r][c]) for c in range(p.n)] for r in range(p.n)]
            found += 1

            prefix = f"{puzzle_id} " if puzzle_id else ""
            if args.num_solutions != 0:
                if args.print_format == "grid":
                    buffer.append(f"{prefix}{render_grid_flat(sol)}")
                elif args.print_format == "string":
                    buffer.append(f"{prefix}{serialize_to_string(p, sol)}")
                elif args.print_format == "all":
                    buffer.append(f"--- Solution #{found} {prefix}---\n{render_ascii_frame(p.n, sol, p.clues)}\n{serialize_to_string(p, sol)}")

            if args.num_solutions > 0 and found >= args.num_solutions:
                break
            flat_grid = [grid_vars[r][c] for r in range(p.n) for c in range(p.n)]
            flat_sol = [sol[r][c] for r in range(p.n) for c in range(p.n)]
            model.AddForbiddenAssignments(flat_grid, [tuple(flat_sol)])

    # FIX: If no solutions were found, report it explicitly rather than remaining silent
    if found == 0:
        prefix = f"{puzzle_id} " if puzzle_id else ""
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
