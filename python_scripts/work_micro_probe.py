#!/usr/bin/env python3
"""Optional in-solver sampled CPU-time probes, for plausibility only.

Run from a fresh clone. Builds a separate executable with timer hooks; never
use its timings as the regression target or in a tuning objective.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess

from calibrate_work import COUNTER_NAMES, DEFAULT_DATASETS, read_puzzles
from tuning_work_runtime import DEFAULT_MODEL, load_model

ROOT = Path(__file__).resolve().parents[1]


def micro_record(lines):
    probes = []
    for line in lines:
        if not line.startswith("WORK_MICRO v1 "):
            continue
        parts = dict(word.split("=", 1) for word in line.split()[2:])
        index = int(parts["counter"])
        if index not in range(len(COUNTER_NAMES)):
            raise ValueError("Unknown micro counter id")
        probes.append({
            "counter": COUNTER_NAMES[index],
            "calls": int(parts["calls"]),
            "samples": int(parts["samples"]),
            "ticks": int(parts["ticks"]),
            "ticks_per_second": int(parts["clock_ticks_per_second"]),
        })
    return probes


def summarize(records, model):
    aggregated = defaultdict(lambda: [0, 0, 0])
    for record in records:
        slot = aggregated[record["counter"]]
        slot[0] += record["calls"]
        slot[1] += record["samples"]
        slot[2] += record["ticks"] / record["ticks_per_second"]
    return {
        counter: {
            "calls": calls, "samples": samples, "sampled_cpu_seconds": seconds,
            "sampled_seconds_per_package": seconds / samples if samples else None,
            "regression_seconds_per_count": model["seconds_per_count"][counter],
            "interpretation": "CPU clock includes begin/end overhead; not a cost ratio",
        } for counter, (calls, samples, seconds) in sorted(aggregated.items())
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--puzzles-per-size", type=int, default=16)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "scratch" / "work_micro_probe.json")
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    if args.puzzles_per_size < 1:
        parser.error("puzzles-per-size must be positive")
    model, digest = load_model(args.model)
    subprocess.run(["make", "INSTRUMENT=1", "MICRO_TIMING=1"], cwd=ROOT, check=True)
    binary = ROOT / "skyscraper_solver_work_micro"
    puzzles = read_puzzles(DEFAULT_DATASETS, args.puzzles_per_size)
    records = []
    for puzzle in puzzles:
        mode = 0 if puzzle["size"] == 7 else 1
        cmd = [str(binary), "-s", str(mode), puzzle["clue"]]
        if puzzle["grid"]:
            cmd.append(puzzle["grid"])
        completed = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True,
            check=True, timeout=args.timeout)
        records.extend(micro_record(completed.stdout.splitlines()))
    result = {
        "purpose": "Experimental plausibility check, NOT fitted coefficients",
        "timer": "sampled process CPU clock, every 64th package",
        "model_sha256": digest,
        "model_source_git_commit": model["source_git_commit"],
        "puzzles": len(puzzles),
        "probes": summarize(records, model),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Experimental micro timing results: {args.output}")


if __name__ == "__main__":
    main()
