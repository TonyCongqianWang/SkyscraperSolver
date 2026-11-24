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
import subprocess
from pathlib import Path
import tempfile

from calibrate_work import (
    COUNTER_NAMES, SCHEMA, ROOT, build, execute, read_puzzles, puzzle_mode,
)
from work_model_export import load_compact_model
from work_section_plausibility import TIMED_SECTIONS, summarize_plausibility, timed_affine_fit

VALIDATION_DATASETS = (
    "puzzle_bank/spsa_datasets/le7_val.txt",
    "puzzle_bank/spsa_datasets/size8_val.txt",
    "puzzle_bank/spsa_datasets/size9_val.txt",
)


def validate_model(model):
    if model.get("usable_for_tuning") is False:
        raise ValueError("Incomplete work model: unresolved merged group allocation")
    if model.get("fit") != "pooled" or model.get("counter_schema") != SCHEMA:
        raise ValueError("Independent micro check requires the pooled v1 model")
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


def verify_splits(summary, collinearity, model, tolerance=2.0,
                  unresolved_groups=()):
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
    unresolved_groups = set(unresolved_groups)
    for call, section in summary.get("sections", {}).items():
        volume = section.get("volume_counter")
        if volume is None:
            continue
        fitted = section["timed_affine_fit"]
        call_weight = model["seconds_per_count"][call]
        volume_weight = model["seconds_per_count"][volume]
        predicted_ratio = (volume_weight / call_weight
                           if call_weight > 0 else None)
        timed_ratio = fitted.get("seconds_per_volume_relative_to_call")
        shared_group = (membership.get(call) is not None
                        and membership.get(call) == membership.get(volume))
        if shared_group and membership.get(call) in unresolved_groups:
            predicted_ratio = None  # Timed result exists, split cannot be judged.
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


def verify_all_merged_groups(controlled, collinearity, model,
                             tolerance=2.0, unresolved_groups=()):
    """Check measured per-member cost ratios for EVERY merged group."""
    from work_micro_constraints import controlled_member_costs
    costs, diagnostics = controlled_member_costs(controlled)
    unresolved_groups = set(unresolved_groups)
    result = {}
    for group in collinearity.get("merged_groups", []):
        members = group["members"]
        ref = members[0]
        estimates = {}
        if ref in costs:
            estimates[ref] = 1.0
            for name in members[1:]:
                if name in costs:
                    estimates[name] = costs[name] / costs[ref]
        predicted = model["seconds_per_count"]
        observations = []
        for name in members[1:]:
            modeled_ratio = (predicted[name] / predicted[ref]
                             if predicted[ref] > 0 and group["name"] not in unresolved_groups
                             else None)
            measured_ratio = estimates.get(name)
            if (modeled_ratio is not None and modeled_ratio > 0
                    and measured_ratio is not None and measured_ratio > 0):
                fold = max(measured_ratio / modeled_ratio,
                           modeled_ratio / measured_ratio)
                verdict = "consistent" if fold <= tolerance else "disagrees"
            else:
                fold = None
                verdict = ("zero_fitted_group" if predicted[ref] == 0
                           and measured_ratio is not None
                           and group["name"] not in unresolved_groups
                           else "unresolved")
            observations.append({
                "reference": ref, "counter": name,
                "measured_ratio": measured_ratio,
                "model_ratio": modeled_ratio,
                "fold_disagreement": fold, "verdict": verdict,
            })
        result[group["name"]] = {
            "members": members,
            "all_independently_timed":
                all(name in costs for name in members),
            "ratios": observations,
        }
    return {
        "groups": result,
        "groups_total": len(result),
        "groups_fully_measured": sum(
            g["all_independently_timed"] for g in result.values()),
        "consistent_comparisons": sum(
            edge["verdict"] == "consistent" for g in result.values()
            for edge in g["ratios"]),
        "disagreeing_comparisons": sum(
            edge["verdict"] == "disagrees" for g in result.values()
            for edge in g["ratios"]),
        "counter_diagnostics": diagnostics,
    }


def verify_model(model, collinearity, puzzles, cc="gcc", timeout=30,
                 unresolved_groups=()):
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
        "split_verification": verify_splits(
            overall, collinearity, model,
            unresolved_groups=unresolved_groups),
    }


def controlled_microbench(cc="gcc", repeats=200000, rounds=3):
    """Measure every known merged operation, independently of puzzle traces.

    Affine call/volume pairs use repeated real operations at different sizes.
    Other counters are isolated with the exact underlying C operation.
    The output retains each independent round for uncertainty diagnostics.
    """
    if repeats < 1000 or rounds < 1:
        raise ValueError("Invalid microbenchmark repetition count")
    source = ROOT / "python_scripts" / "work_micro_controlled.c"
    records = []
    with tempfile.TemporaryDirectory(prefix="sky_controlled_micro_") as temp:
        binary = Path(temp) / "controlled_micro"
        sources = [str(path) for path in sorted((ROOT / "src").glob("*.c"))
                   if path.name != "main.c"]
        command = ([cc, "-Wall", "-Wextra", "-Werror", "-O2", "-flto",
                    "-I", str(ROOT / "src"), str(source)]
                   + sources + ["-o", str(binary)])
        subprocess.run(command, check=True, cwd=ROOT, capture_output=True,
                       text=True)
        # Check the reported DP scan units against the real counters on
        # every invocation of the controlled benchmark. Keep instrumentation
        # out of the actual CPU timing binary.
        checked_binary = Path(temp) / "controlled_micro_checked"
        checked_command = (command[:-2] + ["-DWORK_INSTRUMENTED",
                            "-o", str(checked_binary)])
        subprocess.run(checked_command, check=True, cwd=ROOT,
                       capture_output=True, text=True)
        subprocess.run([str(checked_binary), "1000", "0"], check=True,
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
        for round_number in range(rounds):
            completed = subprocess.run(
                [str(binary), str(repeats), str(round_number)], check=True,
                cwd=ROOT, capture_output=True, text=True, timeout=120)
            for line in completed.stdout.splitlines():
                if not line.startswith("WORK_BENCH "):
                    continue
                parts = line.split()
                if parts[:2] != ["WORK_BENCH", "v1"]:
                    raise ValueError("Unknown controlled microbenchmark version")
                fields = dict(field.split("=", 1) for field in parts[2:])
                if int(fields["round"]) != round_number:
                    raise ValueError("Controlled microbenchmark round mismatch")
                if fields["kind"] == "individual":
                    record = {
                        "kind": "individual", "counter": fields["counter"],
                        "round": round_number, "units": int(fields["units"]),
                        "cpu_seconds": float(fields["cpu_seconds"]),
                    }
                    if fields.get("timing_scope") == "paired_residual":
                        record.update({
                            "timing_scope": fields["timing_scope"],
                            "gross_cpu_seconds": float(fields["gross_cpu_seconds"]),
                            "nested_cpu_seconds": float(fields["nested_cpu_seconds"]),
                            "nested_invalidation_attempts_per_unit": int(
                                fields["nested_invalidation_attempts_per_unit"]),
                            "nested_domain_invalidations_per_unit": int(
                                fields["nested_domain_invalidations_per_unit"]),
                            "nested_dirty_enqueues_per_unit": int(
                                fields["nested_dirty_enqueues_per_unit"]),
                        })
                    records.append(record)
                elif fields["kind"] == "affine":
                    section = fields["section"]
                    if section not in TIMED_SECTIONS:
                        raise ValueError("Unexpected affine benchmark section")
                    records.append({
                        "kind": "affine", "section": section,
                        "round": round_number, "calls": int(fields["calls"]),
                        "volume": int(fields["volume"]),
                        "cpu_seconds": float(fields["cpu_seconds"]),
                    })
                else:
                    raise ValueError("Unknown controlled microbenchmark kind")
    # Require a separate benchmark for EVERY original member of the known
    # merged counter groups. A newly merged group requires a new C benchmark.
    from work_micro_constraints import controlled_member_costs
    costs, diagnostics = controlled_member_costs(
        {"rounds": rounds, "raw_measurements": records},
        expected_names=COUNTER_NAMES)
    return {
        "method": "real_C_operations_controlled_independent_repetitions",
        "compile_flags": ["-O2", "-flto"],
        "repeats_per_point": repeats,
        "rounds": rounds,
        "raw_measurements": records,
        "counter_costs_seconds": costs,
        "counter_diagnostics": diagnostics,
        "coverage": {
            "expected_counters": len(COUNTER_NAMES),
            "accepted_counters": sum(
                x["status"] == "accepted" for x in diagnostics.values()),
            "not_benchmarked": sorted(
                n for n, x in diagnostics.items()
                if x["reason"] == "not_benchmarked"),
            "insufficient_timing_evidence": sorted(
                n for n, x in diagnostics.items()
                if x["reason"] == "insufficient_timing_evidence"),
            "unstable": sorted(
                n for n, x in diagnostics.items()
                if x["reason"] == "unstable"),
        },
        "sections": {
            name: {
                "volume_counter": volume, "observations": sum(
                    r["kind"] == "affine" and r["section"] == name
                    for r in records),
                "timed_affine_fit": timed_affine_fit([
                    (r["cpu_seconds"], r["calls"], r["volume"])
                    for r in records if r["kind"] == "affine"
                    and r["section"] == name]),
            }
            for name, volume in TIMED_SECTIONS.items()
        },
    }


def run_verification(model_path, collinearity_path, output,
                     puzzles_per_size=32, seed=1072, cc="gcc", timeout=None,
                     datasets=VALIDATION_DATASETS, controlled_repeats=200000,
                     controlled_rounds=3, controlled_result=None,
                     diagnostic_model=None, unresolved_groups=()):
    model_path = Path(model_path)
    model = (diagnostic_model if diagnostic_model is not None
             else load_compact_model(model_path))
    unresolved_groups = tuple(unresolved_groups)
    collinearity = json.loads(Path(collinearity_path).read_text(encoding="utf-8"))
    if puzzles_per_size < 1:
        raise ValueError("puzzles_per_size must be positive")
    puzzles = read_puzzles(datasets, puzzles_per_size, seed=seed)
    if not puzzles:
        raise ValueError("No validation puzzles for micro verification")
    if diagnostic_model is None:
        report = verify_model(model, collinearity, puzzles, cc, timeout)
    else:
        report = verify_model(model, collinearity, puzzles, cc, timeout,
                              unresolved_groups=unresolved_groups)
    report["status"] = ("completed_with_unresolved_allocation"
                        if unresolved_groups else "complete")
    report["validation_basis"] = ("pooled_merged_regression_projection"
                                  if diagnostic_model is not None
                                  else "allocated_per_counter_model")
    report["unresolved_groups"] = list(unresolved_groups)
    controlled = (controlled_result if controlled_result is not None
                  else controlled_microbench(
                      cc, controlled_repeats, controlled_rounds))
    report["controlled_microbenchmark"] = controlled
    report["controlled_split_verification"] = verify_splits(
        controlled, collinearity, model,
        unresolved_groups=unresolved_groups)
    report["controlled_all_group_verification"] = verify_all_merged_groups(
        controlled, collinearity, model,
        unresolved_groups=unresolved_groups)
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
    parser.add_argument("--timeout", type=float, default=None,
                        help="Optional per-solver timeout; default: unlimited")
    parser.add_argument("--controlled-repeats", type=int, default=200000)
    parser.add_argument("--controlled-rounds", type=int, default=3)
    args = parser.parse_args()
    result = run_verification(
        args.model, args.collinearity, args.output,
        args.puzzles_per_size, args.seed, args.cc, args.timeout,
        controlled_repeats=args.controlled_repeats,
        controlled_rounds=args.controlled_rounds)
    print(json.dumps({
        "puzzles": result["puzzle_counts_by_size"],
        "plausibility_score": result["overall"]["plausibility_score"],
        "split_verification": result["split_verification"],
        "controlled_split_verification": result["controlled_split_verification"],
        "controlled_all_group_verification": {
            key: result["controlled_all_group_verification"][key]
            for key in ("groups_total", "groups_fully_measured",
                        "consistent_comparisons", "disagreeing_comparisons")
        },
        "report": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
