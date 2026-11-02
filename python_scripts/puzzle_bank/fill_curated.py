#!/usr/bin/env python3
"""Fill curated quotas directly from minimal puzzles without candidate files.

Randomly samples the Cartesian product of extra edge clues and extra givens.
Existing curated entries are preserved; newly verified entries are appended.
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python_scripts.puzzle_bank.curate import LEVELS, difficulty
from python_scripts.puzzle_bank.generate_unique import clues_for, verify


def fill_size(size, quotas, source, target, solver, timeout, seed, attempts):
    with source.open(encoding="utf-8") as file:
        bank = json.load(file)
    rng = random.Random(seed + size)
    existing = json.loads(target.read_text()) if target.exists() else {}
    buckets = existing.get("difficulties", {name: [] for name in LEVELS})
    for name in LEVELS:
        buckets.setdefault(name, [])
    seen = {(tuple(v["clues"]), tuple(v["givens"]), v["solution_group_id"])
            for rows in buckets.values() for v in rows}
    wanted = {name: quotas.get(name, 0) for name in LEVELS}
    cap = 15000
    for name, count in wanted.items():
        if not isinstance(count, int) or count < 0:
            raise ValueError(f"invalid quota {size}/{name}: {count}")

    def done():
        return all(len(buckets[name]) >= wanted[name] for name in LEVELS)

    # A bucket can grow beyond its minimum, up to cap, while any quota is unmet.
    # Revisit minimal puzzles with fresh samples; don't stop after a single sweep.
    # Reset the stall counter for each new puzzle in a positive-quota bucket
    # below 1.5x its minimum, even if its minimum is already satisfied.
    stall_limit = 1000
    stalled = 0
    pool = [(group, base) for group in bank["groups"]
            for base in group["puzzles"]]
    if not done() and not pool:
        print(f"size {size}: no minimal puzzles available", file=sys.stderr)

    while pool and not done() and stalled < stall_limit:
        rng.shuffle(pool)
        for group, base in pool:
            if done() or stalled >= stall_limit:
                break
            solution = group["canonical_solution"]
            n = size
            grid = [solution[i*n:(i+1)*n] for i in range(n)]
            full = clues_for(grid)
            missing = [i for i, x in enumerate(base["clues"]) if not x]
            empty = [i for i, x in enumerate(base["givens"]) if not x]
            max_givens = max(0, n*n//3 - sum(bool(x) for x in base["givens"]))
            for _ in range(attempts):
                if done() or stalled >= stall_limit:
                    break
                # Each trial chooses a random position in the 2D density grid.
                add_clues = rng.randrange(len(missing) + 1)
                add_givens = rng.randrange(min(len(empty), max_givens) + 1)
                clue_indices = rng.sample(missing, add_clues)
                given_indices = rng.sample(empty, add_givens)
                clues = base["clues"][:]
                givens = base["givens"][:]
                for i in clue_indices:
                    clues[i] = full[i]
                for i in given_indices:
                    givens[i] = solution[i]
                key = (tuple(clues), tuple(givens), group["id"])
                # Repeated candidates and unsuccessful verifications are tries.
                stalled += 1
                if key in seen:
                    continue
                seen.add(key)
                result = verify(solver, clues, givens, timeout)
                if result is None or result[0] != 1:
                    continue
                nodes, main_nodes = result[1:3]
                grade = difficulty(nodes, main_nodes)
                if len(buckets[grade]) >= cap:
                    continue
                counts_as_progress = (wanted[grade] > 0 and
                                      2 * len(buckets[grade]) < 3 * wanted[grade])
                # Deterministic identity, distinct across sweeps and reruns.
                digest = hashlib.sha256(repr(key).encode("utf-8")).hexdigest()[:20]
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
    args = parser.parse_args()
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
            cfg["seed"], cfg["max_attempts_per_minimal"])
        print(f"size {size}: " + ", ".join(
            f"{name}={s['selected']}/{s['quota']}"
            for name, s in summary["sizes"][str(size)].items()), flush=True)
    (args.output / "statistics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
