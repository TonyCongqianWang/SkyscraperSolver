"""Compact, self-contained pooled work model for tuning and deployment.

Only the pooled fit is exported. Diagnostic size-specific fits and individual
run measurements remain in the large calibration report / raw JSONL files.
This module deliberately has no third-party dependencies.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path


FORMAT = "skyscraper-work-model"
FORMAT_VERSION = 1


def make_compact_model(report, source_file=None, created_at=None):
    """Flatten fitted merged groups into weights on original counters.

    Since each merged feature is the SUM of its constituent raw counters,
    assigning its fitted coefficient to every member is exactly equivalent
    to full-model prediction. A zero coefficient is assigned to every
    excluded constant/non-identifiable counter.
    """
    provenance = report["provenance"]
    fit = report["fits"]["all"]
    if fit["status"] != "fitted":
        raise ValueError("Pooled fit is not available")
    model = fit["coefficients"]
    names = provenance["counter_schema"]
    if len(names) != len(set(names)) or not names:
        raise ValueError("Counter names must be nonempty and unique")
    grouped = model["collinearity"]["groups"]
    coefficients = model["seconds_per_count"]
    allocation = report.get("pooled_unmerging")
    if provenance["schema"] != "v1":
        raise ValueError("Unsupported work counter schema")
    if not allocation:
        raise ValueError("Pooled model requires measured post-fit unmerging")
    allocation_weights = allocation["seconds_per_count"]
    complete = allocation.get("all_merged_groups_resolved") is True
    unresolved_counters = []
    weights = dict.fromkeys(names, 0.0)
    seen = set()
    for group in grouped:
        group_name = group["name"]
        members = group["members"]
        if not members or group_name not in coefficients:
            raise ValueError(f"Invalid group: {group_name}")
        if group.get("aggregation") != "sum_raw_counts":
            raise ValueError(f"Unsupported grouping: {group_name}")
        weight = float(coefficients[group_name])
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("Invalid nonnegative coefficient")
        for name in members:
            if name not in weights or name in seen:
                raise ValueError(f"Unknown or repeated raw counter: {name}")
            seen.add(name)
            raw_weight = allocation_weights.get(name)
            if raw_weight is None and not complete:
                weights[name] = None
                unresolved_counters.append(name)
                continue
            if not isinstance(raw_weight, (int, float)):
                raise ValueError(f"Missing independently measured split: {name}")
            if not math.isfinite(raw_weight) or raw_weight < 0:
                raise ValueError(f"Invalid allocated counter weight: {name}")
            weights[name] = raw_weight
    if set(coefficients) != {g["name"] for g in grouped}:
        raise ValueError("Fitted coefficient and group names disagree")
    if set(allocation_weights) != seen:
        raise ValueError("Allocated coefficients must cover all fitted counters")
    if complete and unresolved_counters:
        raise ValueError("Resolved allocation cannot contain null weights")
    intercept = float(model["intercept_seconds"])
    if not math.isfinite(intercept) or intercept < 0:
        raise ValueError("Invalid nonnegative intercept")
    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()
    allocated_validation = allocation.get("held_out_validation") if complete else None
    validation = (allocated_validation if allocated_validation is not None
                  else fit["validation"])
    score_keys = (
        "samples", "mae_seconds", "r2", "ranking_accuracy",
        "clear_ranking_accuracy", "clear_ranking_coverage",
        "clear_ranking_pairs", "macro_clear_ranking_accuracy",
        "within_puzzle_mae_seconds", "within_puzzle_r2",
    )
    score = {name: validation[name] for name in score_keys
             if name in validation}
    allocated_by_size = allocation.get("held_out_validation_by_size")
    by_size = ({"size" + size: metrics for size, metrics in
                (allocated_by_size or {}).items()}
               if allocated_validation is not None
               else report.get("pooled_validation_by_size", {}))
    short_size = {
        name: {metric: metrics.get(metric) for metric in (
            "mae_seconds", "r2", "clear_ranking_accuracy",
            "clear_ranking_coverage", "within_puzzle_r2")}
        for name, metrics in by_size.items()
    }
    result = {
        "format": FORMAT,
        "status": "complete" if complete else "incomplete",
        "usable_for_tuning": complete,
        "unresolved_counters": sorted(unresolved_counters),
        "unresolved_groups": allocation.get("unresolved_groups", []),
        "warnings": report.get("warnings", []),
        "format_version": FORMAT_VERSION,
        "created_at_utc": created_at,
        "source_calibration_file": str(source_file) if source_file else None,
        "source_git_commit": provenance.get("git_commit"),
        "counter_schema": provenance["schema"],
        "training_sizes": sorted(int(k) for k, n in
                                 provenance["puzzles_per_size"].items() if n),
        "max_solutions_by_size": provenance.get("max_solutions_by_size"),
        "training_observations": report["sample_counts"]["train"],
        "validation_observations": report["sample_counts"]["validation"],
        "dataset_sha256": {path: checksum for path, checksum
                           in provenance["datasets"]},
        "compiler": provenance.get("compiler"),
        "fit": "pooled",
        "intercept_seconds": intercept,
        "seconds_per_count": weights,
        "hyperparameters": {
            "ridge_alpha": model["ridge_alpha"],
            "contrast_weight": model["contrast_weight"],
        },
        "held_out_score": score,
        "held_out_score_basis": ("allocated_model" if allocated_validation is not None
                                 else "pooled_merged_regression"),
        "allocated_validation_status": ("evaluated" if allocated_validation is not None
                                        else "not_evaluated"),
        "held_out_score_by_size": short_size,
        "dropped_counters": sorted(set(names) - seen),
        "coefficient_allocation_method": allocation["method"],
        "merged_group_coefficients": dict(coefficients),
        "merged_group_allocations": [
            {key: val for key, val in group.items()
             if key != "timing_evidence"} for group in allocation["groups"]],
        "regression_held_out_score": fit["validation"],
        "counter_semantics": "fixed event counts and actual variable volumes",
        "objective": "predicted_seconds",
    }
    if provenance.get("seed") is not None:
        # Store as decimal text to preserve all 64 bits in JSON consumers.
        result["calibration_seed"] = str(provenance["seed"])
    counts = {n for n in provenance["puzzles_per_size"].values() if n}
    if len(counts) == 1:
        result["calibration_puzzles_per_size"] = next(iter(counts))
    if provenance.get("validation_fraction") is not None:
        result["calibration_validation_fraction"] = provenance["validation_fraction"]
    # Guard against serialization of NaN/Infinity in a deployment artifact.
    json.dumps(result, allow_nan=False)
    return result



def pooled_validation_projection(report):
    """In-memory representation of the *fitted pooled* predictor for validation.

    Each merged sum-of-counts feature is expanded algebraically. These
    projected coefficients are NOT individually calibrated and must never
    be exported as tuning coefficients.
    """
    fit = report["fits"]["all"]
    if fit["status"] != "fitted":
        raise ValueError("Pooled regression is not available for validation")
    coefficients = fit["coefficients"]
    names = report["provenance"]["counter_schema"]
    weights = dict.fromkeys(names, 0.0)
    for group in coefficients["collinearity"]["groups"]:
        for member in group["members"]:
            if member not in weights:
                raise ValueError(f"Unknown fitted counter: {member}")
            weights[member] = coefficients["seconds_per_count"][group["name"]]
    return {
        "fit": "pooled",
        "counter_schema": report["provenance"]["schema"],
        "source_git_commit": report["provenance"].get("git_commit"),
        "intercept_seconds": coefficients["intercept_seconds"],
        "seconds_per_count": weights,
        "diagnostic_projection": True,
    }


def make_collinearity_export(report, source_file=None, created_at=None):
    """Preserve pooled merged counter dependencies for microbenchmark design.

    Only the *training-derived* collinearity analysis of the pooled fit is
    included. Correlation does not imply an instruction-level cost ratio.
    """
    fit = report["fits"]["all"]
    if fit["status"] != "fitted":
        raise ValueError("Pooled fit is not available")
    coefficients = fit["coefficients"]
    analysis = coefficients["collinearity"]
    schema = report["provenance"]["counter_schema"]
    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()

    # Also validates raw-counter membership, groups and coefficients.
    compact = make_compact_model(report, source_file, created_at)
    allocated_groups = {
        group["group"]: group
        for group in report.get("pooled_unmerging", {}).get("groups", [])}
    groups = []
    for group in analysis["groups"]:
        if len(group["members"]) < 2:
            continue
        allocated = allocated_groups.get(group["name"])
        groups.append({
            "name": group["name"],
            "members": list(group["members"]),
            "status": (allocated.get("status", "resolved")
                       if allocated else "unresolved"),
            "reason": allocated.get("reason") if allocated else "Not allocated",
            "missing_or_unstable_counters": (
                allocated.get("missing_or_unstable_counters", [])
                if allocated else list(group["members"])),
            "aggregation": group["aggregation"],
            "seconds_per_merged_count":
                coefficients["seconds_per_count"][group["name"]],
            "allocated_member_seconds_per_count": (
                allocated["seconds_per_original_count"] if allocated else None),
            "measured_cost_ratios": (
                allocated["member_cost_ratios"] if allocated else None),
            "timing_evidence": (
                allocated["timing_evidence"] if allocated else None),
            "max_abs_training_prediction_drift_seconds": (
                allocated["max_abs_training_prediction_drift_seconds"]
                if allocated else None),
        })
    output = {
        "format": "skyscraper-work-collinearity",
        "status": compact["status"],
        "usable_for_tuning": compact["usable_for_tuning"],
        "unresolved_groups": compact["unresolved_groups"],
        "warnings": compact["warnings"],
        "format_version": 1,
        "created_at_utc": created_at,
        "source_calibration_file": str(source_file) if source_file else None,
        "source_git_commit": compact["source_git_commit"],
        "counter_schema": report["provenance"]["schema"],
        "counter_names": list(schema),
        "fit": "pooled",
        "correlation_threshold": analysis["correlation_threshold"],
        "dependency_tolerance": analysis["dependency_tolerance"],
        "method": analysis["method"],
        "merge_events": analysis["merge_events"],
        "correlated_pairs": analysis["correlated_pairs"],
        "merged_groups": groups,
        "constant_counters": analysis["constant_counters"],
        "constant_merged_groups": analysis["constant_merged_groups"],
        "rank_before": analysis["rank_before"],
        "rank_after": analysis["rank_after"],
        "dropped_counters": compact["dropped_counters"],
        "allocation_method": compact["coefficient_allocation_method"],
        "controlled_counter_costs_seconds": report.get(
            "pooled_unmerging", {}).get("controlled_counter_costs_seconds"),
        "controlled_counter_diagnostics": report.get(
            "pooled_unmerging", {}).get("controlled_counter_diagnostics"),
        "assumption": analysis["cost_assumption"],
        "purpose": "Design microbenchmarks to identify independent relative costs",
        "interpretation": (
            "Correlated counters were summed for a provisional fit. "
            "The fitted coefficient is NOT a measured ratio of operation costs."
        ),
    }
    json.dumps(output, allow_nan=False)
    return output


def export_collinearity(report, target, source_file=None, created_at=None):
    result = make_collinearity_export(report, source_file, created_at)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, sort_keys=True, indent=2,
                                 allow_nan=False) + "\n", encoding="utf-8")
    return result


def predict_seconds(model, counters):
    """Predict runtime using a v1 compact artifact and original raw counts."""
    if model.get("format") != FORMAT or model.get("format_version") != FORMAT_VERSION:
        raise ValueError("Unsupported compact model format")
    if model.get("usable_for_tuning") is False:
        raise ValueError("Unresolved calibration: incomplete model is not usable for tuning")
    weights = model["seconds_per_count"]
    if set(counters) != set(weights):
        raise ValueError("Counter schema mismatch: provide all counters")
    return model["intercept_seconds"] + sum(
        value * counters[name] for name, value in weights.items())


def load_compact_model(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def export_compact_model(report, target, source_file=None, created_at=None):
    model = make_compact_model(report, source_file, created_at)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(model, sort_keys=True, indent=2,
                                 allow_nan=False) + "\n", encoding="utf-8")
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="Existing detailed work_calibration.json")
    parser.add_argument("--output", type=Path,
                        help="Destination (default: input.model.json)")
    parser.add_argument("--collinearity-output", type=Path,
                        help="Diagnostic output (default: input.collinearity.json)")
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    target = args.output or args.input.with_suffix(".model.json")
    timestamp = datetime.now(timezone.utc).isoformat()
    export_compact_model(report, target, args.input, timestamp)
    collinearity_target = (args.collinearity_output
                           or args.input.with_suffix(".collinearity.json"))
    export_collinearity(report, collinearity_target, args.input, timestamp)
    print(f"Exported pooled model to {target}")
    print(f"Exported pooled collinearity to {collinearity_target}")


if __name__ == "__main__":
    main()
