#!/usr/bin/env python3
"""Independently check pooled counter cost splits on SPSA validation puzzles.

Runs the optional sampled-timing solver *after* fitting. It measures real
sections on puzzles that were never used for calibration/inner selection.
This is observational section micro-timing, NOT a synthetic isolated-loop
benchmark: clock overhead and correlated nested operations can bias ratios.
It never updates the model or chooses its hyperparameters.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from calibrate_work import (
    COUNTER_NAMES, ROOT, build, execute, read_puzzles, puzzle_mode,
)
from work_model_export import load_compact_model
from work_section_plausibility import summarize_plausibility

VALIDATION_DATASETS = (
    "puzzle_bank/spsa_datasets/le7_val.txt",
    "puzzle_bank/spsa_datasets/size8_val.txt",
    "puzzle_bank/spsa_datasets/size9_val.txt",
)


def validate_model(model):
    if model.get("fit") != "pooled" or model.get("counter_schema") != "v3":
        raise ValueError("Independent micro check requires the new pooled v3 model")
    if set(model.get("seconds_per_count", {})) != set(COUNTER_NAMES):
        raise ValueError("Model counter schema does not match solver")


def group_model(model):
    """Expand compact raw coefficients into singleton feature groups."""
    return {
        "seconds_per_count": model["seconds_per_count"],
        "collinearity": {"groups": [
            {"name": name, "members": [name], "aggregation": "sum_raw_counts"}
            for name in COUNTER_NAMES
        ]},
    }


def verify_splits(summary, collinearity, model, tolerance=2.0):
    """Check whether timed *relative* costs support modeled split candidates.

    A merged equal-weight group proposes a cost ratio of 1. Otherwise test
    ratio of distinct fitted raw weights. Missing/zero weights and
    unidentifiable timed affine fits yield explicit 'unresolved', not passes.
    """
    membership = {}
    for group in collinearity.get("merged_groups", []):
        for name in group["members"]:
            membership[name] = group["name"]
    results = {}
    for call, section in summary["sections"].items():
        volume = section["volume_counter"]
        fitted = section["timed_affine_fit"]
        call_weight = model["seconds_per_count"][call]
        volume_weight = model["seconds_per_count"][volume]
        predicted_ratio = (volume_weight / call_weight
                           if call_weight > 0 else None)
        timed_ratio = fitted.get("seconds_per_volume_relative_to_call")
        shared_group = (membership.get(call) is not None
                        and membership.get(call) == membership.get(volume))
        verdict = "unresolved"
        fold_error = None
        if (fitted.get("identifiable") and timed_ratio is not None
                and timed_ratio > 0 and predicted_ratio is not None
                and predicted_ratio > 0):
            fold_error = max(timed_ratio / predicted_ratio,
                             predicted_ratio / timed_ratio)
            verdict = "consistent" if fold_error <= tolerance else "disagrees"
        results[call] = {
            "volume_counter": volume,
            "merged_together": shared_group,
            "merged_group": membership.get(call) if shared_group else None,
            "modeled_volume_per_call_cost_ratio": predicted_ratio,
            "timed_volume_per_call_cost_ratio": timed_ratio,
            "ratio_disagreement_factor": fold_error,
            "verdict": verdict,
            "timed_fit_identifiable": fitted.get("identifiable", False),
        }
    checked = [x for x in results.values() if x["verdict"] != "unresolved"]
    return {
        "ratio_tolerance_factor": tolerance,
        "checked_splits": len(checked),
        "consistent_splits": sum(x["verdict"] == "consistent" for x in checked),
        "disagreeing_splits": sum(x["verdict"] == "disagrees" for x in checked),
        "unresolved_splits": len(results) - len(checked),
        "splits": results,
        "interpretation": "CPU-clock ratios are independent checks, not constraints or replacement coefficients",
    }


def verify_model(model, collinearity, puzzles, cc="gcc", timeout=30):
    validate_model(model)
    if collinearity.get("counter_schema") != model["counter_schema"]:
        raise ValueError("Model and collinearity schemas differ")
    rows = []
    with tempfile.TemporaryDirectory(prefix="sky_micro_verify_") as directory:
        binary, _ = build(Path(directory), {"name": "micro_validation",
                                           "parameters": {}}, True, cc,
                          ["-DWORK_MICRO_TIMING"])
        for puzzle in puzzles:
            mode = puzzle_mode(puzzle, None)
            elapsed, solutions, nodes, counters, sections = execute(
                binary, puzzle, mode, timeout, include_micro=True)
            rows.append({
                "size": puzzle["size"], "identity": puzzle["identity"],
                "dataset": puzzle["dataset"], "line": puzzle["line"],
                "solutions": solutions, "nodes": nodes,
                "elapsed_timed_seconds": elapsed,
                "counters": counters, "micro_sections": sections,
            })
    grouped = group_model(model)
    overall = summarize_plausibility(rows, grouped, COUNTER_NAMES)
    return {
        "model_schema": model["counter_schema"],
        "model_source_commit": model.get("source_git_commit"),
        "datasets": sorted({p["dataset"] for p in puzzles}),
        "puzzles": len(rows),
        "measurement": "sampled CPU clock time in independently held-out SPSA validation puzzles",
        "overall": overall,
        "by_size": {
            "size" + str(n): summarize_plausibility(
                [r for r in rows if r["size"] == n], grouped, COUNTER_NAMES)
            for n in (7, 8, 9)
        },
        "split_verification": verify_splits(overall, collinearity, model),
    }


def run_verification(model_path, collinearity_path, output,
                     puzzles_per_size=32, seed=1072, cc="gcc", timeout=30,
                     datasets=VALIDATION_DATASETS):
    model_path = Path(model_path)
    model = load_compact_model(model_path)
    collinearity = json.loads(Path(collinearity_path).read_text(encoding="utf-8"))
    if puzzles_per_size < 1:
        raise ValueError("puzzles_per_size must be positive")
    puzzles = read_puzzles(datasets, puzzles_per_size, seed=seed)
    if not puzzles:
        raise ValueError("No validation puzzles for micro verification")
    report = verify_model(model, collinearity, puzzles, cc, timeout)
    report["model_file_sha256"] = hashlib.sha256(model_path.read_bytes()).hexdigest()
    report["puzzle_counts_by_size"] = {
        str(n): sum(p["size"] == n for p in puzzles) for n in (7, 8, 9)
    }
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True,
                                 allow_nan=False) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path,
                        default=ROOT / "scratch" / "work_calibration.model.json")
    parser.add_argument("--collinearity", type=Path,
                        default=ROOT / "scratch" / "work_calibration.collinearity.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "scratch" / "work_calibration.micro.json")
    parser.add_argument("--puzzles-per-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=1072)
    parser.add_argument("--cc", default="gcc")
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    result = run_verification(
        args.model, args.collinearity, args.output,
        args.puzzles_per_size, args.seed, args.cc, args.timeout)
    print(json.dumps({
        "puzzles": result["puzzle_counts_by_size"],
        "plausibility_score": result["overall"]["plausibility_score"],
        "split_verification": result["split_verification"],
        "report": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
