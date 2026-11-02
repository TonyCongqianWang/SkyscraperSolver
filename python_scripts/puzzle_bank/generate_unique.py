#!/usr/bin/env python3
"""Generate versioned minimal and augmented unique puzzle banks with the native solver."""
import argparse
import json
import math
import random
import re
import subprocess
import shlex
import sys
import time
import traceback

# Reuse the same cycle-switch sampler as the SPSA dataset generator.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python_scripts.dataset_generation.generator import (
    MCMCLatinSquareSampler,
)

def visibility(line):
    highest = count = 0
    for v in line:
        if v > highest:
            highest = v
            count += 1
    return count

def square_symmetries(grid):
    """All eight D4 board symmetries; do not relabel heights."""
    def rotate(g):
        return [list(row) for row in zip(*g[::-1])]

    def reflect(g):
        return [row[::-1] for row in g]

    result = []
    current = [row[:] for row in grid]
    for _ in range(4):
        result.append(current)
        result.append(reflect(current))
        current = rotate(current)
    return result


def canonical_square(grid):
    """Lexicographically least row-major solution under D4."""
    flat = min(tuple(v for row in g for v in row)
               for g in square_symmetries(grid))
    n = len(grid)
    return [list(flat[i*n:(i+1)*n]) for i in range(n)]


def solution_key(grid):
    return tuple(v for row in canonical_square(grid) for v in row)


def clues_for(g):
    n = len(g)
    return ([visibility([g[r][c] for r in range(n)]) for c in range(n)]
       + [visibility([g[r][c] for r in range(n-1, -1, -1)]) for c in range(n)]
       + [visibility(g[r]) for r in range(n)]
       + [visibility(g[r][::-1]) for r in range(n)])

def verify(binary, clues, cells, timeout, *, diagnose=False):
    try:
        p = subprocess.run([str(binary), "-s", "2", " ".join(map(str, clues)),
                            " ".join(map(str, cells))], text=True, capture_output=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if diagnose:
            raise RuntimeError(f"Solver timed out after {timeout}s for clues={clues}, cells={cells}") from exc
        return None
    if p.returncode:
        if diagnose:
            raise RuntimeError(f"Solver exited {p.returncode} for clues={clues}, cells={cells}\\nstdout={p.stdout}\\nstderr={p.stderr}")
        return None
    m = re.search(r"^Solutions found:\s*(\d+)\s*$", p.stdout, re.M)
    nodes = re.search(r"^Nodes visited:\s*(\d+)\s*$", p.stdout, re.M)
    main_nodes = re.search(r"^Main nodes visited:\s*(\d+)\s*$", p.stdout, re.M)
    if not m or not nodes or not main_nodes:
        if diagnose:
            raise RuntimeError(f"Solver output could not be parsed for clues={clues}, cells={cells}\\nstdout={p.stdout}\\nstderr={p.stderr}")
        return None
    return (int(m[1]), int(nodes[1]), int(main_nodes[1]))

def print_failure_diagnostics(binary, ident, label, minimal, variant, cells,
                              solution, timeout, seed, attempt, original_error=None):
    """Emit all context and reproducible solver runs to stderr before failing."""
    def fmt(values):
        return " ".join(map(str, values))

    print("\\n" + "=" * 76, file=sys.stderr)
    print("UNIQUE PUZZLE BANK — VERIFICATION FAILURE", file=sys.stderr)
    print(f"Puzzle: {ident} | variant: {label} | attempt: {attempt} | seed: {seed}",
          file=sys.stderr)
    print(f"Minimal clues: {minimal}", file=sys.stderr)
    print(f"Variant clues: {variant}", file=sys.stderr)
    print(f"Given cells:   {cells}", file=sys.stderr)
    print(f"Known solution: {solution}", file=sys.stderr)
    if original_error is not None:
        print(f"Original failure: {original_error!r}", file=sys.stderr)
    for name, clue_set in (("minimal", minimal), ("failing variant", variant)):
        for limit in (2, 0):
            command = [str(binary), "-s", str(limit), fmt(clue_set), fmt(cells)]
            print(f"\\n{name}, -s {limit}: {shlex.join(command)}", file=sys.stderr)
            try:
                run = subprocess.run(command, capture_output=True, text=True,
                                     timeout=timeout, check=False)
                print(f"Exit code: {run.returncode}", file=sys.stderr)
                print("stdout:\\n" + run.stdout, file=sys.stderr)
                if run.stderr:
                    print("stderr:\\n" + run.stderr, file=sys.stderr)
            except subprocess.TimeoutExpired as exc:
                print(f"TIMEOUT after {timeout}s: {exc}", file=sys.stderr)
    print("=" * 76, file=sys.stderr, flush=True)


def weighted_removal_order(candidates, solved, full, rng, weight, rate=0.25):
    """Preserve grid/clue cost priority, bias ties with exponential weights."""
    n = len(solved)
    def priority(item):
        _, is_cell, idx = item
        value = solved[idx // n][idx % n] if is_cell else full[idx]
        preference = (math.exp(-rate * value) if is_cell
                      else math.exp(rate * abs(value - 3)))
        # Weighted sampling without replacement; more preferred entries first.
        return rng.random() ** (1.0 / preference)
    return sorted(candidates, key=lambda item: (-item[0], -priority(item)))


def minimize(binary, full, solved, rng, timeout, weight):
    n = len(solved)
    clues, cells = full[:], [0] * (n*n)
    if verify(binary, clues, cells, timeout) is None:
        return None
    if verify(binary, clues, cells, timeout)[0] != 1:
        positions = list(range(n*n))
        rng.shuffle(positions)
        for i in positions:
            cells[i] = solved[i//n][i%n]
            check = verify(binary, clues, cells, timeout)
            if check and check[0] == 1:
                break
        else:
            return None
    candidates = [(weight, 1, i) for i,v in enumerate(cells) if v]
    candidates += [(1, 0, i) for i,v in enumerate(clues) if v]
    candidates = weighted_removal_order(candidates, solved, full, rng, weight)
    for _, is_cell, i in candidates:
        target = cells if is_cell else clues
        old = target[i]
        target[i] = 0
        test = verify(binary, clues, cells, timeout)
        if not test or test[0] != 1:
            target[i] = old
    test = verify(binary, clues, cells, timeout)
    return (clues, cells, test[1], test[2]) if test and test[0] == 1 else None

def unique_samples(positions, count, rng, samples_per_step):
    """Choose up to four distinct unordered subsets for a given density."""
    if count == 0:
        yield ()
        return
    seen = set()
    # Small candidate spaces cannot provide four distinct subsets.
    # Avoid an unbounded retry loop when the space is exhausted.
    import math
    target = min(samples_per_step, math.comb(len(positions), count))
    attempts = 0
    while len(seen) < target and attempts < max(50, target * 30):
        attempts += 1
        key = tuple(sorted(rng.sample(positions, count)))
        if key not in seen:
            seen.add(key)
            yield key


def generate_variants(binary, ident, clues, cells, full, solution, minimal_nodes,
                      rng, timeout, seed, attempt, samples_per_step):
    """Vary extra edge clues and extra givens independently."""
    n = len(solution)
    missing_clues = [i for i, value in enumerate(clues) if not value]
    available_cells = [i for i, value in enumerate(cells) if not value]
    max_given_additions = min(len(available_cells), n*n//3 - sum(bool(x) for x in cells))
    variants = []
    seen = set()

    def append(label, new_clues, new_cells, known_nodes=None):
        key = (tuple(new_clues), tuple(new_cells))
        if key in seen:
            return
        seen.add(key)
        if known_nodes is None:
            try:
                result = verify(binary, new_clues, new_cells, timeout, diagnose=True)
                if result[0] != 1:
                    raise RuntimeError(f"Variant {label} found {result[0]} solutions")
            except Exception as exc:
                print_failure_diagnostics(
                    binary, ident, label, clues, new_clues, new_cells,
                    solution, timeout, seed, attempt, exc)
                raise RuntimeError(f"Verification failed for {ident}/{label}") from exc
            nodes, main_nodes = result[1], result[2]
        else:
            nodes, main_nodes = known_nodes
        variants.append({
            "label": label, "clues": new_clues[:], "givens": new_cells[:],
            "clue_count": sum(bool(x) for x in new_clues),
            "given_count": sum(bool(x) for x in new_cells),
            "nodes_visited": nodes,
            "main_nodes_visited": main_nodes,
        })

    append("minimal", clues, cells, minimal_nodes)
    for added in range(1, len(missing_clues) + 1):
        for index, subset in enumerate(unique_samples(
                missing_clues, added, rng, samples_per_step), 1):
            variant = clues[:]
            for i in subset:
                variant[i] = full[i]
            label = "full_clues" if added == len(missing_clues) else f"clues_plus_{added}_{index}"
            append(label, variant, cells)
    for added in range(1, max(0, max_given_additions) + 1):
        for index, subset in enumerate(unique_samples(
                available_cells, added, rng, samples_per_step), 1):
            new_cells = cells[:]
            for i in subset:
                new_cells[i] = solution[i//n][i%n]
            append(f"givens_plus_{added}_{index}", clues, new_cells)
    return variants


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--size", type=int, required=True, choices=range(4, 10))
    ap.add_argument("--count", type=int, default=5,
                    help="Number of distinct solutions up to board symmetry")
    ap.add_argument("--attempts", type=int, default=100,
                    help="Maximum sampled solutions, including repeats")
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--weight", type=int, default=5)
    ap.add_argument("--timeout", type=float, default=10)
    ap.add_argument("--burn-in", type=int, default=100000)
    ap.add_argument("--gap", type=int, default=100)
    ap.add_argument("--batch-size", type=int, default=10000)
    ap.add_argument("--reseed-interval", type=int, default=250)
    ap.add_argument("--variants-per-step", type=int, default=4)
    ap.add_argument("--minimal-only", action="store_true",
                    help="Skip candidate variants; write minimal puzzles only")
    ap.add_argument("--solver", type=Path, default=ROOT/"skyscraper_solver")
    ap.add_argument("--output", type=Path, default=ROOT/"puzzle_bank"/"unique"/"v2")
    args = ap.parse_args()
    if (min(args.count, args.attempts, args.weight, args.timeout,
            args.gap, args.batch_size, args.reseed_interval, args.variants_per_step) <= 0
            or args.burn_in < 0):
        ap.error("positive parameters required (burn-in may be zero)")
    # Exact number of D4 orbits for n=4; for other sizes the known
    # Latin-square totals are conservative upper bounds on orbit counts.
    latin_square_counts = {
        4: 576,
        5: 161280,
        6: 812851200,
        7: 61479419904000,
        8: 108776032459082956800,
        9: 5524751496156892842531225600,
    }
    limit = 74 if args.size == 4 else latin_square_counts[args.size]
    if args.count > limit:
        print(f"Size {args.size}: reducing count from {args.count} to {limit} "
              "(maximum possible distinct solution groups).", flush=True)
        args.count = limit
    binary = args.solver.resolve()
    if not binary.is_file():
        ap.error("Build the native solver using make first")
    rng = random.Random(args.seed)
    sampler = MCMCLatinSquareSampler(args.size, seed=args.seed,
                                    burn_in=args.burn_in, gap=args.gap,
                                    batch_size=args.batch_size,
                                    reseed_interval=args.reseed_interval)
    minimal_groups = {}
    candidate_groups = {}
    seen_puzzles = set()
    last_report = time.monotonic()

    for attempt in range(1, args.attempts + 1):
        if len(minimal_groups) >= args.count:
            break
        now = time.monotonic()
        if now - last_report >= 60:
            print(f"Size {args.size}: {len(minimal_groups)}/{args.count} groups, "
                  f"{len(seen_puzzles)} puzzles, {attempt - 1} samples", flush=True)
            last_report = now
        solution = canonical_square(sampler.next_square().tolist())
        key = tuple(v for row in solution for v in row)
        full = clues_for(solution)
        item = minimize(binary, full, solution, rng, args.timeout, args.weight)
        if item is None:
            continue
        clues, cells, nodes, main_nodes = item
        puzzle_key = (key, tuple(clues), tuple(cells))
        if puzzle_key in seen_puzzles:
            continue
        seen_puzzles.add(puzzle_key)
        new_group = key not in minimal_groups
        if new_group:
            group_id = f"s{args.size}-{len(minimal_groups)+1:05d}"
            minimal_groups[key] = {
                "id": group_id, "canonical_solution": list(key), "puzzles": []}
            if not args.minimal_only:
                candidate_groups[key] = {
                "id": group_id, "canonical_solution": list(key), "puzzles": []}
        group = minimal_groups[key]
        ident = group["id"] + f"-p{len(group['puzzles'])+1:03d}"
        base = {
            "id": ident, "size": args.size, "clues": clues, "givens": cells,
            "solution": list(key), "clue_count": sum(bool(v) for v in clues),
            "given_count": sum(bool(v) for v in cells),
            "cost": sum(bool(v) for v in clues) + args.weight*sum(bool(v) for v in cells),
            "nodes_visited": nodes,
            "main_nodes_visited": main_nodes,
        }
        group["puzzles"].append(base)
        if not args.minimal_only:
            variants = generate_variants(
                binary, ident, clues, cells, full, solution, (nodes, main_nodes), rng,
                args.timeout, args.seed, attempt, args.variants_per_step)
            candidate_groups[key]["puzzles"].append({
                "id": ident, "size": args.size, "variants": variants,
                "difficulty_matched": False})
        if new_group and len(minimal_groups) % 50 == 0:
            print(f"Size {args.size}: {len(minimal_groups)}/{args.count} groups, "
                  f"{len(seen_puzzles)} puzzles, {attempt} samples", flush=True)
            last_report = time.monotonic()

    if len(minimal_groups) != args.count:
        raise SystemExit(
            f"Insufficient distinct solution groups: {len(minimal_groups)}/{args.count} "
            f"after {args.attempts} attempts; no output written")
    out = args.output
    (out/"minimal").mkdir(parents=True, exist_ok=True)
    if not args.minimal_only:
        (out/"candidates").mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema_version": 2, "size": args.size, "count": args.count,
        "puzzle_count": len(seen_puzzles), "seed": args.seed,
        "sampler": {"method": "cycle_switch_mcmc", "burn_in": args.burn_in,
                    "gap": args.gap, "batch_size": args.batch_size,
                    "reseed_interval": args.reseed_interval},
        "mcmc_reseeds": sampler.reseeds,
        "symmetry": "D4_board_only", "canonical_rep": "lexicographically_smallest_grid",
        "uniqueness": "verified by native solver -s 2", "cell_weight": args.weight,
    }
    (out/"minimal"/f"size_{args.size}.json").write_text(
        json.dumps({**metadata, "groups": list(minimal_groups.values())}, indent=2) + "\n")
    if not args.minimal_only:
        (out/"candidates"/f"size_{args.size}.json").write_text(
            json.dumps({**metadata, "status": "uncalibrated",
                        "variants_per_step": args.variants_per_step,
                        "max_given_fraction": "1/3",
                        "groups": list(candidate_groups.values())}, indent=2) + "\n")
    print(f"Wrote grouped MCMC puzzle banks to {out}")


if __name__ == "__main__":
    main()
