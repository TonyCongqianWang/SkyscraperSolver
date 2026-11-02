#!/usr/bin/env python3
"""Curate v2 candidate banks into independently versioned, capped public banks.

Candidate JSON stays offline (Git LFS/release assets). Curated JSON includes only
selected variants and source references, never the complete candidate corpus.
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

LEVELS = ("very_easy", "easy", "medium", "hard", "very_hard", "extreme", "impossible")
SCHEMA = 1


def difficulty(nodes, main_nodes):
    """Main nodes take precedence; in particular main=2 => hard..very_hard.

    The original thresholds leave gaps (e.g. 4000 nodes and main=1).
    Complete those cases with main-dependent difficulty floors/ceilings:
    1: total-based through very_hard; 2: hard..very_hard;
    3..8: hard..extreme; 9+: impossible.
    """
    if nodes < 0 or main_nodes < 1:
        raise ValueError("node counts must be nonnegative, main nodes >= 1")
    if main_nodes > 8:
        return "impossible"
    if main_nodes >= 3:
        if nodes <= 800:
            return "hard"
        if nodes <= 1600:
            return "very_hard"
        return "extreme"
    if main_nodes == 2:
        return "hard" if nodes <= 800 else "very_hard"
    if nodes <= 100:
        return "very_easy"
    if nodes <= 200:
        return "easy"
    if nodes <= 400:
        return "medium"
    if nodes <= 800:
        return "hard"
    return "very_hard"


def curate_size(path, output, limit, seed):
    rng = random.Random(seed)
    with path.open(encoding="utf-8") as source:
        bank = json.load(source)
    n = bank["size"]
    buckets = {level: [] for level in LEVELS}
    encountered = Counter()
    groups_seen = set()

    for group in bank["groups"]:
        group_id = group["id"]
        solution = group["canonical_solution"]
        for base in group["puzzles"]:
            minimal_id = base["id"]
            variants = base.get("variants", [base])
            for v in variants:
                label = v.get("label", "minimal")
                nodes = v["nodes_visited"]
                main = v["main_nodes_visited"]
                grade = difficulty(nodes, main)
                encountered[grade] += 1
                k = encountered[grade]
                # Uniform reservoir sample: no bias from file order or variant count.
                subset = buckets[grade]
                place = len(subset) if len(subset) < limit else rng.randrange(k)
                if place >= limit:
                    continue
                row = {
                    "id": minimal_id + ":" + label,
                    "solution_group_id": group_id,
                    "minimal_puzzle_id": minimal_id,
                    "candidate_label": label,
                    "canonical_solution": solution,
                    "clues": v["clues"],
                    "givens": v["givens"],
                    "clue_count": v.get("clue_count", sum(bool(x) for x in v["clues"])),
                    "given_count": v.get("given_count", sum(bool(x) for x in v["givens"])),
                    "nodes_visited": nodes,
                    "main_nodes_visited": main,
                }
                if place == len(subset):
                    subset.append(row)
                else:
                    subset[place] = row

    stats = {}
    for grade in LEVELS:
        subset = buckets[grade]
        stats[grade] = {
            "available": encountered[grade],
            "selected": len(subset),
            "selection_fraction": round(len(subset) / encountered[grade], 6)
            if encountered[grade] else 0,
            "min_nodes": min((v["nodes_visited"] for v in subset), default=None),
            "max_nodes": max((v["nodes_visited"] for v in subset), default=None),
            "min_main_nodes": min((v["main_nodes_visited"] for v in subset), default=None),
            "max_main_nodes": max((v["main_nodes_visited"] for v in subset), default=None),
        }

    output.mkdir(parents=True, exist_ok=True)
    public = {
        "schema_version": SCHEMA,
        "size": n,
        "difficulty_policy": "main_node_override_v1",
        "source_bank": "unique/v2/candidates",
        "curated_version": "v1",
        "max_per_difficulty": limit,
        "seed": seed,
        "statistics": stats,
        "difficulties": buckets,
    }
    (output / f"size_{n}.json").write_text(
        json.dumps(public, separators=(",", ":")) + "\n", encoding="utf-8")
    return {
        "size": n,
        "solution_groups_in_source": len(bank["groups"]),
        "minimal_puzzles_in_source": sum(len(g["puzzles"]) for g in bank["groups"]),
        "candidate_variants_in_source": sum(encountered.values()),
        "statistics": stats,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path("puzzle_bank/unique/v2/candidates"))
    parser.add_argument("--output", type=Path,
                        default=Path("puzzle_bank/curated/v1"))
    parser.add_argument("--sizes", type=int, nargs="+", default=list(range(4, 10)))
    parser.add_argument("--max-per-band", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=12345)
    args = parser.parse_args()
    if args.max_per_band < 1:
        parser.error("--max-per-band must be positive")
    report = {"schema_version": SCHEMA, "curated_version": "v1",
              "difficulty_policy": "main_node_override_v1", "sizes": {}}
    for size in args.sizes:
        path = args.source / f"size_{size}.json"
        print(f"Curating {path}", flush=True)
        info = curate_size(path, args.output, args.max_per_band, args.seed + size)
        report["sizes"][str(size)] = info
        print(f"  {info['candidate_variants_in_source']} candidates -> "
              f"{sum(v['selected'] for v in info['statistics'].values())} curated",
              flush=True)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "statistics.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
