#!/usr/bin/env python3
"""Generate lightweight public availability metadata from curated size banks."""
import argparse
import json
from pathlib import Path

LEVELS = ("very_easy", "easy", "medium", "hard", "very_hard", "extreme", "impossible")


def build_metadata(directory):
    sizes = {}
    for size in range(4, 10):
        path = directory / f"size_{size}.json"
        bank = json.loads(path.read_text(encoding="utf-8"))
        if bank.get("schema_version") != 1 or bank.get("size") != size:
            raise ValueError(f"Unexpected curated bank schema or size: {path}")
        buckets = bank.get("difficulties")
        if not isinstance(buckets, dict):
            raise ValueError(f"Missing difficulty buckets: {path}")
        if set(buckets) != set(LEVELS):
            raise ValueError(f"Unexpected difficulty buckets: {path}")
        sizes[str(size)] = {}
        for level in LEVELS:
            puzzles = buckets[level]
            if not isinstance(puzzles, list):
                raise ValueError(f"Invalid bucket {level}: {path}")
            sizes[str(size)][level] = len(puzzles)
            reported = bank.get("statistics", {}).get(level, {}).get("selected")
            if reported is not None and reported != len(puzzles):
                raise ValueError(f"Count mismatch for {size}/{level}: {reported} != {len(puzzles)}")
    return {"schema_version": 1, "curated_version": "v1", "sizes": sizes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path("puzzle_bank/curated/v1"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    metadata = build_metadata(args.directory)
    destination = args.output or args.directory / "metadata.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
