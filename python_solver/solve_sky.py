import argparse
from z3 import sat, Or
from parser import parse_puzzle_input
from solver_core import create_base_solver
from renderer import render_grid_flat, render_ascii_frame, serialize_to_string

def main():
    parser = argparse.ArgumentParser(description="Skyscraper Puzzle SMT Solver Engine.")
    parser.add_argument("input", type=str, nargs="+", help="Input properties.")
    parser.add_argument("-s", "--num_solutions", type=int, default=1, help="Max solutions to track.")
    parser.add_argument("-p", "--print_format", type=str, choices=["grid", "string", "all"], default="all")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output destination file path.")
    args = parser.parse_args()

    p = parse_puzzle_input(args.input)
    solver, grid_vars = create_base_solver(p, randomize=True)
    found = 0
    buffer = []

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

    if args.output:
        f = open(args.output, "w", encoding="utf-8")
    else:
        f = None
    print(f"Total Unique Solutions Found: {found}\n", file=f)
    for solution in buffer:
        print(f"{solution}\n", file=f)
    f.close() if f else None

if __name__ == "__main__":
    main()
