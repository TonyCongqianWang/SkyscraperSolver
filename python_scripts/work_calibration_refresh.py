"""Refresh post-fit allocation without fitting regression or rerunning native timing."""
import json
from pathlib import Path

import calibrate_work as cal
from work_micro_constraints import allocate_merged_coefficients
from work_micro_probe import controlled_microbench
from work_model_export import export_compact_model, export_collinearity


def refresh(args):
    source = json.loads(args.micro_only.read_text())
    compact = source.get("format") == "skyscraper-work-model"
    if compact:
        from benchmark_work_calibration import original_split, collect, resolve_seed
        seed = resolve_seed(source, args.seed)
        count = source.get("calibration_puzzles_per_size", args.puzzles_per_size)
        fraction = source.get("calibration_validation_fraction", args.validation_fraction)
        train, _ = original_split(seed, count, fraction, tuple(source["dataset_sha256"]))
        print(f"Refresh seed: {seed}", flush=True)
        for puzzle in train:
            if source["dataset_sha256"].get(puzzle["dataset"]) != puzzle["dataset_sha256"]:
                raise ValueError("Dataset checksum differs from compact model")
        coefficients = source["merged_group_coefficients"]
        pooled = {"intercept_seconds": source["intercept_seconds"],
                  "seconds_per_count": coefficients,
                  "collinearity": {"groups": [
                      {"name": name, "members": name.split("+"),
                       "aggregation": "sum_raw_counts"} for name in coefficients]}}
        # Original raw observations are unavailable: regenerate counter totals,
        # not native timings. CPU-limited prefixes may differ on this machine.
        rows = collect(train, cal.variants(train, True, seed), args.cc,
                       args.timeout, cal.DEFAULT_CPU_LIMITS,
                       source["max_solutions_by_size"], counters_only=True)
        section = {}
    else:
        if source["provenance"]["counter_schema"] != list(cal.COUNTER_NAMES):
            raise ValueError("Incompatible detailed calibration schema")
        pooled = source["fits"]["all"]["coefficients"]
        rows = [r for r in source["samples"] if r["split"] == "train"]
        heldout = [r for r in source["samples"] if r["split"] == "validation"]
        section = (source.get("section_timing_plausibility") or {}).get("train", {})
        if not rows or not heldout:
            raise ValueError("Detailed report lacks original train/validation observations")
    required = {n for g in pooled["collinearity"]["groups"]
                if len(g["members"]) > 1 and pooled["seconds_per_count"][g["name"]] > 0
                for n in g["members"]}
    timing = controlled_microbench(args.cc, args.micro_repeats, args.micro_rounds,
                                   max_repeats=args.micro_max_repeats, required_names=required)
    allocation = allocate_merged_coefficients(pooled, rows, timing, section)
    complete = allocation["all_merged_groups_resolved"]
    target = args.model_output or cal.ROOT / "scratch" / "work_calibration.refreshed.model.json"
    if target.resolve() == args.micro_only.resolve():
        raise ValueError("Refusing to overwrite source calibration")
    weights = {n: allocation["seconds_per_count"].get(n, 0.0) for n in cal.COUNTER_NAMES}
    if compact:
        source.update({"seconds_per_count": weights, "status": "complete" if complete else "incomplete",
                       "usable_for_tuning": complete, "provisional_allocation": False,
                       "unresolved_groups": allocation["unresolved_groups"],
                       "unresolved_counters": sorted(n for n, w in weights.items() if w is None),
                       "warnings": allocation["warnings"],
                       "merged_group_allocations": allocation["groups"],
                       "coefficient_allocation_method": allocation["method"],
                       "held_out_score_basis": "original_pooled_regression_not_refreshed_model",
                       "allocated_validation_status": "not_evaluated",
                       "allocation_training_basis": "regenerated_counter_observations",
                       "held_out_score": source["regression_held_out_score"]})
        source.pop("held_out_score_by_size", None)
        source.pop("allocated_validation_evidence", None)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(source, indent=2, allow_nan=False) + "\n")
    else:
        if complete:
            allocated = {"intercept_seconds": pooled["intercept_seconds"], "seconds_per_count": weights}
            prov = source["provenance"]
            def metrics(data):
                return cal.diagnostics(data, allocated, prov.get("ranking_noise_z", 2),
                                       prov.get("ranking_min_delta_seconds", 5e-5))
            allocation["held_out_validation"] = metrics(heldout)
            allocation["held_out_validation_by_size"] = {
                str(n): metrics([r for r in heldout if r["size"] == n]) for n in (7, 8, 9)}
        source["pooled_unmerging"] = allocation
        source["controlled_microbenchmark"] = timing
        source["warnings"] = allocation["warnings"]
        export_compact_model(source, target, args.micro_only)
        export_collinearity(source, args.collinearity_output or target.with_suffix(".collinearity.json"),
                            args.micro_only)
    target.with_suffix(".timing.json").write_text(json.dumps(timing, indent=2, allow_nan=False) + "\n")
    print(f"Saved refreshed model to {target}; fully allocated: {complete}")
