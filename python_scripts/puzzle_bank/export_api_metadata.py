#!/usr/bin/env python3
"""Validate curated banks and publish shard files plus compact statistics."""
import argparse
import json
from pathlib import Path
import shutil

LEVELS = (
    "very_easy", "easy", "medium", "hard", "very_hard",
    "extreme", "extreme_plus", "extreme_plus_plus",
)
METRICS = ("nodes_visited", "main_nodes_visited", "clue_count", "given_count")


def distribution(values):
    if not values:
        return None
    ordered = sorted(values)
    count = len(ordered)

    def percentile(fraction):
        position = (count - 1) * fraction
        lo = int(position)
        hi = min(lo + 1, count - 1)
        return round(ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo), 2)

    minimum, maximum = ordered[0], ordered[-1]
    bins = min(16, maximum - minimum + 1)
    histogram = [0] * bins
    for value in values:
        index = min(bins - 1, (value - minimum) * bins // (maximum - minimum + 1))
        histogram[index] += 1
    return {
        "min": minimum, "max": maximum,
        "mean": round(sum(values) / count, 2),
        "p10": percentile(.10), "p25": percentile(.25),
        "p50": percentile(.50), "p75": percentile(.75),
        "p90": percentile(.90),
        "histogram": histogram,
    }


def details(rows):
    if not rows:
        return {"count": 0, "metrics": {metric: None for metric in METRICS}}
    return {
        "count": len(rows),
        "metrics": {
            metric: distribution([p[metric] for p in rows])
            for metric in METRICS
        },
    }


def export_curated(source, destination):
    """Return the metadata and statistics for the generated static shards."""
    source, destination = Path(source), Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    metadata = {"schema_version": 1, "curated_version": "v1",
                "difficulties": list(LEVELS), "sizes": {}}
    stats = {"schema_version": 1, "curated_version": "v1",
             "sizes": {}, "details": {"all": {}}}
    all_levels = {level: [] for level in LEVELS}
    report_path = source / "statistics.json"
    report = json.loads(report_path.read_text()) if report_path.is_file() else {}

    for size in range(4, 10):
        source_file = source / f"size_{size}.json"
        bank = json.loads(source_file.read_text(encoding="utf-8"))
        if bank.get("schema_version") != 1 or bank.get("size") != size:
            raise ValueError(f"Invalid curated bank schema or size: {source_file}")
        if bank.get("curated_version") not in ("v1", "v2"):
            raise ValueError(f"Incorrect curated version: {source_file}")
        groups = bank.get("difficulties")
        if not isinstance(groups, dict) or set(groups) != set(LEVELS):
            raise ValueError(f"Incorrect difficulty buckets: {source_file}")
        metadata["sizes"][str(size)] = {}
        stats["sizes"][str(size)] = {}
        stats["details"][str(size)] = {}

        for level in LEVELS:
            puzzles = groups[level]
            if not isinstance(puzzles, list):
                raise ValueError(f"Invalid {size}/{level} bucket")
            count = len(puzzles)
            quota = bank.get("quotas", {}).get(level, 0)
            reported = report.get("sizes", {}).get(str(size), {}).get(level, {})
            if reported and reported.get("selected") != count:
                raise ValueError(f"Count mismatch: {size}/{level}")
            metadata["sizes"][str(size)][level] = count
            stats["sizes"][str(size)][level] = {"selected": count, "quota": quota}
            stats["details"][str(size)][level] = details(puzzles)
            all_levels[level].extend(puzzles)
            if not count:
                continue
            folder = destination / str(size)
            folder.mkdir(exist_ok=True)
            shard = {
                "schema_version": 1, "curated_version": "v1",
                "size": size, "difficulty": level,
                "source_bank": "unique/v1/minimal",
                "difficulty_policy": bank.get("difficulty_policy"),
                "puzzles": puzzles,
            }
            (folder / f"{level}.json").write_text(
                json.dumps(shard, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
    for level, puzzles in all_levels.items():
        stats["details"]["all"][level] = details(puzzles)
    for filename, payload in (("metadata.json", metadata), ("statistics.json", stats)):
        (destination / filename).write_text(
            json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8"
        )
    return metadata, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path("puzzle_bank/curated/v1"))
    parser.add_argument("--output", type=Path, default=Path("public/assets/puzzles/curated/v1"))
    args = parser.parse_args()
    export_curated(args.directory, args.output)


if __name__ == "__main__":
    main()
