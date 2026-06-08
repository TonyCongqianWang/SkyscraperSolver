import argparse
from parser import parse_puzzle_input
from renderer import render_grid_flat, render_ascii_frame, serialize_to_string

def main():
    parser = argparse.ArgumentParser(description="Skyscraper Puzzle Solver Engine.")
    parser.add_argument("input", type=str, nargs="+", help="Input properties.")
    parser.add_argument("-b", "--backend", type=str, choices=["z3", "cpsat"], default="z3", help="Solver backend to use.")
    parser.add_argument("-s", "--num_solutions", type=int, default=1, help="Max solutions to track.")
    parser.add_argument("-p", "--print_format", type=str, choices=["grid", "string", "all"], default="all")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output destination file path.")
    args = parser.parse_args()

    p = parse_puzzle_input(args.input)

    # --- Backend Routing ---
    if args.backend == "z3":
        from solver_core_z3 import create_base_solver
        solver, grid_vars = create_base_solver(p, randomize=True)
    elif args.backend == "cpsat":
        from solver_core_cpsat import create_base_solver
        solver, model, grid_vars = create_base_solver(p, randomize=True)

    found = 0
    buffer = []

    while True:
        # --- Solve and Extract ---
        if args.backend == "z3":
            from z3 import sat, Or
            if solver.check() != sat:
                break
            m = solver.model()
            sol = [[m[grid_vars[r][c]].as_long() for c in range(p.n)] for r in range(p.n)]

        elif args.backend == "cpsat":
            from ortools.sat.python import cp_model
            status = solver.Solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                break
            sol = [[solver.Value(grid_vars[r][c]) for c in range(p.n)] for r in range(p.n)]

        found += 1

        # --- Formatting ---
        if args.num_solutions != 0:
            if args.print_format == "grid":
                buffer.append(render_grid_flat(sol))
            elif args.print_format == "string":
                buffer.append(serialize_to_string(p, sol))
            elif args.print_format == "all":
                buffer.append(f"--- Solution #{found} ---\n{render_ascii_frame(p.n, sol, p.clues)}\n{serialize_to_string(p, sol)}")

        if args.num_solutions > 0 and found >= args.num_solutions:
            break

        # --- Block Previous Solution ---
        if args.backend == "z3":
            solver.add(Or([grid_vars[r][c] != sol[r][c] for r in range(p.n) for c in range(p.n)]))
        elif args.backend == "cpsat":
            flat_grid = [grid_vars[r][c] for r in range(p.n) for c in range(p.n)]
            flat_sol = [sol[r][c] for r in range(p.n) for c in range(p.n)]
            model.AddForbiddenAssignments(flat_grid, [tuple(flat_sol)])

    # --- Output ---
    f = open(args.output, "w", encoding="utf-8") if args.output else None
    print(f"Total Unique Solutions Found: {found}\n", file=f)
    for solution in buffer:
        print(f"{solution}\n", file=f)
    if f:
        f.close()

if __name__ == "__main__":
    main()
