#!/usr/bin/env python3
"""Offline summary of candidate or curated puzzle banks, for analysis and static indexes."""
import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


PERCENTILES = (10, 25, 50, 75, 90, 95, 99)


def describe(values):
    if not values:
        return None
    ordered = sorted(values)
    n = len(ordered)
    result = {"count": n, "min": ordered[0],
              "mean": round(sum(ordered) / n, 3)}
    for p in PERCENTILES:
        position = (n - 1) * p / 100
        lo = int(position)
        hi = min(lo + 1, n - 1)
        result["median" if p == 50 else f"p{p}"] = round(
            ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo), 3)
    result["max"] = ordered[-1]
    return result


def hist(values):
    counts = Counter("0" if v == 0 else str(v.bit_length() - 1) for v in values)
    return dict(sorted(counts.items(), key=lambda item: int(item[0])))


def category(label):
    if label == "minimal":
        return "minimal"
    if label == "full_clues":
        return "full_clues"
    if label.startswith("clues_plus_"):
        return "added_clues"
    if label.startswith("givens_plus_"):
        return "added_givens"
    return "other"


def summary(records, include_hist=True):
    total = [r[0] for r in records]
    main = [r[1] for r in records]
    result = {
        "count": len(records),
        "total_nodes": describe(total),
        "main_nodes": describe(main),
        "main_fraction": describe([m / t for t, m in records if t > 0]),
    }
    if include_hist:
        result["total_nodes_log2_histogram"] = hist(total)
        result["main_nodes_log2_histogram"] = hist(main)
    return result


def analyze(data):
    by_family = defaultdict(list)
    by_clues = defaultdict(list)
    by_givens = defaultdict(list)
    by_pair = defaultdict(list)
    by_added_clues = defaultdict(list)
    by_added_givens = defaultdict(list)
    all_records = []
    puzzle_count = 0

    for group in data["groups"]:
        for puzzle in group["puzzles"]:
            puzzle_count += 1
            variants = puzzle.get("variants", [puzzle])
            baseline = next((v for v in variants if v.get("label") == "minimal"),
                            variants[0])
            base_clues = baseline.get("clue_count", sum(bool(x) for x in baseline["clues"]))
            base_givens = baseline.get("given_count", sum(bool(x) for x in baseline["givens"]))
            for v in variants:
                clues = v.get("clue_count", sum(bool(x) for x in v["clues"]))
                givens = v.get("given_count", sum(bool(x) for x in v["givens"]))
                record = (v["nodes_visited"], v["main_nodes_visited"])
                all_records.append(record)
                by_family[category(v.get("label", "minimal"))].append(record)
                by_clues[clues].append(record)
                by_givens[givens].append(record)
                by_pair[(clues, givens)].append(record)
                if clues > base_clues:
                    by_added_clues[clues - base_clues].append(record)
                if givens > base_givens:
                    by_added_givens[givens - base_givens].append(record)

    def breakdown(mapping):
        return {str(k): {"count": len(rows),
                         "total": describe([r[0] for r in rows]),
                         "main": describe([r[1] for r in rows])}
                for k, rows in sorted(mapping.items())}

    pairs = []
    for (clues, givens), rows in sorted(by_pair.items()):
        t = describe([r[0] for r in rows])
        m = describe([r[1] for r in rows])
        pairs.append({"clues": clues, "givens": givens, "count": len(rows),
                      "total_min": t["min"], "total_median": t["median"],
                      "total_p90": t["p90"], "total_max": t["max"],
                      "main_min": m["min"], "main_median": m["median"],
                      "main_p90": m["p90"], "main_max": m["max"]})

    return {
        "size": data["size"],
        "solution_groups": len(data["groups"]),
        "minimal_puzzles": puzzle_count,
        "candidate_variants": len(all_records),
        "all": summary(all_records),
        "families": {k: summary(v) for k, v in sorted(by_family.items())},
        "by_clue_count": breakdown(by_clues),
        "by_given_count": breakdown(by_givens),
        "by_added_clues": breakdown(by_added_clues),
        "by_added_givens": breakdown(by_added_givens),
        "by_clue_given_pair": pairs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path,
                        default=Path("puzzle_bank/unique/v2/candidates"))
    parser.add_argument("--sizes", type=int, nargs="+", default=[4, 5, 6, 7])
    parser.add_argument("--output", type=Path, default=Path("candidate_stats.json"))
    args = parser.parse_args()
    report = {
        "schema": "candidate_statistics_v2",
        "log2_histogram_note": "Bin k covers 2^k through 2^(k+1)-1; bin 0 also includes zero.",
        "sizes": {},
    }
    for size in args.sizes:
        path = args.directory / f"size_{size}.json"
        print(f"Reading {path} ...", flush=True)
        with path.open(encoding="utf-8") as file:
            report["sizes"][str(size)] = analyze(json.load(file))
        print(f"  {report['sizes'][str(size)]['candidate_variants']} variants", flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}", flush=True)


if __name__ == "__main__":
    main()
