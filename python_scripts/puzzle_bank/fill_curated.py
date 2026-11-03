#!/usr/bin/env python3
"""Fill curated quotas directly from minimal puzzles without candidate files.

Randomly samples the Cartesian product of extra edge clues and extra givens.
Existing curated entries are preserved; newly verified entries are appended.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python_scripts.puzzle_bank.curate import LEVELS, difficulty
from python_scripts.puzzle_bank.generate_unique import clues_for, verify


def fill_size(size, quotas, source, target, solver, timeout, seed, attempts, workers=4):
    with source.open(encoding="utf-8") as file:
        bank = json.load(file)
    rng = random.Random(seed + size)
    existing = json.loads(target.read_text()) if target.exists() else {}
    buckets = existing.get("difficulties", {name: [] for name in LEVELS})
    for name in LEVELS:
        buckets.setdefault(name, [])
    # Regrade existing puzzles, including those formerly classified as impossible.
    # Preserve the per-grade cap when migrating old entries.
    regraded = {name: [] for name in LEVELS}
    for rows in buckets.values():
        for puzzle in rows:
            grade = difficulty(puzzle["nodes_visited"], puzzle["main_nodes_visited"])
            if len(regraded[grade]) < 15000:
                regraded[grade].append(puzzle)
    buckets = regraded
    seen = {(tuple(v["clues"]), tuple(v["givens"]), v["solution_group_id"])
            for rows in buckets.values() for v in rows}
    wanted = {name: quotas.get(name, 0) for name in LEVELS}
    cap = 15000
    for name, count in wanted.items():
        if not isinstance(count, int) or count < 0:
            raise ValueError(f"invalid quota {size}/{name}: {count}")

    def done():
        return all(len(buckets[name]) >= wanted[name] for name in LEVELS)

    # A single coordinator owns seen, quotas, and the stall counter.
    # Workers only run the independent native solver subprocesses.
    stall_limit = 10000
    stalled = 0
    pool = [(group, base) for group in bank["groups"]
            for base in group["puzzles"]]
    last_report = time.monotonic()
    met = {name for name in LEVELS
           if wanted[name] > 0 and len(buckets[name]) >= wanted[name]}

    def report(reason):
        nonlocal last_report
        print(f"size {size}: {reason}; " +
              ", ".join(f"{name}={len(buckets[name])}/{wanted[name]}"
                        for name in LEVELS) +
              f"; stalled={stalled}/{stall_limit}", flush=True)
        last_report = time.monotonic()

    if not done() and not pool:
        print(f"size {size}: no minimal puzzles available", file=sys.stderr)

    def candidates():
        # Recycle and reshuffle the source pool indefinitely. Each pass draws
        # fresh random clue/given subsets from the same minimal puzzles.
        while pool:
            rng.shuffle(pool)
            for group, base in pool:
                solution = group["canonical_solution"]
                n = size
                grid = [solution[i*n:(i+1)*n] for i in range(n)]
                full = clues_for(grid)
                missing = [i for i, x in enumerate(base["clues"]) if not x]
                empty = [i for i, x in enumerate(base["givens"]) if not x]
                max_givens = max(0, n*n//3 - sum(bool(x) for x in base["givens"]))
                for _ in range(attempts):
                    add_clues = rng.randrange(len(missing) + 1)
                    add_givens = rng.randrange(min(len(empty), max_givens) + 1)
                    clues = base["clues"][:]
                    givens = base["givens"][:]
                    for i in rng.sample(missing, add_clues):
                        clues[i] = full[i]
                    for i in rng.sample(empty, add_givens):
                        givens[i] = solution[i]
                    key = (tuple(clues), tuple(givens), group["id"])
                    yield group, base, solution, clues, givens, key

    def check(item):
        group, base, solution, clues, givens, key = item
        return item, verify(solver, clues, givens, timeout)

    if pool and not done():
        draws = iter(candidates())
        with ThreadPoolExecutor(max_workers=workers) as executor:
            while not done() and stalled < stall_limit:
                # Keep only one small batch in flight, so all quota and stall
                # decisions remain on the coordinator thread.
                batch = []
                while len(batch) < workers:
                    item = next(draws)
                    if item[5] in seen:
                        batch.append((item, None))
                    else:
                        seen.add(item[5])
                        batch.append((item, True))
                futures = [executor.submit(check, item)
                           if needs_check else None
                           for item, needs_check in batch]
                for (item, needs_check), future in zip(batch, futures):
                    if done() or stalled >= stall_limit:
                        break
                    stalled += 1
                    if future is None:
                        result = None
                    else:
                        _, result = future.result()
                    if result is not None and result[0] == 1:
                        group, base, solution, clues, givens, key = item
                        nodes, main_nodes = result[1:3]
                        grade = difficulty(nodes, main_nodes)
                        if len(buckets[grade]) < cap:
                            counts_as_progress = (wanted[grade] > 0 and
                                2 * len(buckets[grade]) < 3 * wanted[grade])
                            digest = hashlib.sha256(
                                repr(key).encode("utf-8")).hexdigest()[:20]
                            buckets[grade].append({
                                "id": f"{base['id']}:sample_{digest}",
                                "solution_group_id": group["id"],
                                "minimal_puzzle_id": base["id"],
                                "canonical_solution": solution,
                                "candidate_label": "mixed_random",
                                "clues": clues, "givens": givens,
                                "clue_count": sum(bool(x) for x in clues),
                                "given_count": sum(bool(x) for x in givens),
                                "nodes_visited": nodes,
                                "main_nodes_visited": main_nodes,
                            })
                            if counts_as_progress:
                                stalled = 0
                            if wanted[grade] > 0 and grade not in met and \
                                    len(buckets[grade]) >= wanted[grade]:
                                met.add(grade)
                                report(f"{grade} quota met")
                    if time.monotonic() - last_report >= 60:
                        report("periodic progress")
    report("finished" if done() else "stopped")
    if stalled >= stall_limit and not done():
        missing_quotas = {name: wanted[name] - len(buckets[name])
                          for name in LEVELS if len(buckets[name]) < wanted[name]}
        print(f"size {size}: stopped after {stall_limit} draws without "
              f"progress towards unmet quotas: {missing_quotas}",
              file=sys.stderr)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 1, "size": size, "curated_version": "v2",
               "source_bank": "unique/v3/minimal", "difficulty_policy": "main_node_override_v2",
               "quotas": wanted, "max_per_difficulty": cap, "difficulties": buckets}
    target.write_text(json.dumps(payload, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    return {name: {"selected": len(buckets[name]), "quota": wanted[name]}
            for name in LEVELS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "puzzle_bank/curated/v2/quotas.json")
    parser.add_argument("--source", type=Path, default=ROOT / "puzzle_bank/unique/v3/minimal")
    parser.add_argument("--output", type=Path, default=ROOT / "puzzle_bank/curated/v2")
    parser.add_argument("--solver", type=Path, default=ROOT / "skyscraper_solver")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--sizes", nargs="+", type=int, default=list(range(4, 10)))
    parser.add_argument("--workers", type=int, default=4,
                        help="Concurrent native solver checks (default: 4)")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    limits = cfg["sizes"]
    if not 1 <= cfg["max_attempts_per_minimal"] <= 100000:
        parser.error("max_attempts_per_minimal must be 1..100000")
    summary = {"schema_version": 1, "curated_version": cfg["version"], "sizes": {}}
    for size in args.sizes:
        if str(size) not in limits:
            parser.error(f"missing quotas for size {size}")
        summary["sizes"][str(size)] = fill_size(
            size, limits[str(size)], args.source / f"size_{size}.json",
            args.output / f"size_{size}.json", args.solver, args.timeout,
            cfg["seed"], cfg["max_attempts_per_minimal"], args.workers)
        print(f"size {size}: " + ", ".join(
            f"{name}={s['selected']}/{s['quota']}"
            for name, s in summary["sizes"][str(size)].items()), flush=True)
    (args.output / "statistics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
