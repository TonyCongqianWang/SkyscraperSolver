#!/usr/bin/env python3
"""Compare fixed work models against fresh native timings; never fit a model."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import tempfile

import calibrate_work as cal
from tuning_work_runtime import DEFAULT_MODEL, load_model


def collect(puzzles, configurations, cc, timeout, cpu_limits, modes,
            native_repeats=2, counters_only=False):
    from spsa_tune import get_default_theta, get_physical_params, project_constraints
    defaults = get_physical_params(project_constraints(get_default_theta()))
    by_id = {}
    for config in configurations:
        by_id.setdefault(config["puzzle_identity"], []).append(config)
    rows = []
    with tempfile.TemporaryDirectory(prefix="sky_work_validate_") as folder:
        fixed = {"name": "validation", "parameters": {}}
        instr, _ = cal.build(Path(folder), fixed, True, cc, [])
        native = None if counters_only else cal.build(Path(folder), fixed, False, cc, [])[0]
        for puzzle in puzzles:
            for config in by_id[puzzle["identity"]]:
                env = dict(os.environ, **{k: str(v) for k, v in defaults.items()})
                env.update({k: str(v) for k, v in config["parameters"].items()})
                mode = modes[str(puzzle["size"])]
                def run(kind, repeat, binary, include_micro=False,
                        cpu_limit=None, checkpoint=None):
                    return cal.execute(binary, puzzle, mode, timeout,
                        env=cal.checkpoint_environment(env, cpu_limit, checkpoint),
                        return_status=True)
                if counters_only:
                    first = run("instrumented", 0, instr, cpu_limit=cpu_limits[puzzle["size"]])
                    rows.append({"counters": first[3]})
                    continue
                first, times, _, _, status = cal.measure_checkpoint_observation(
                    run, instr, native, None, 1, native_repeats, cpu_limits[puzzle["size"]])
                rows.append({"size": puzzle["size"], "identity": puzzle["identity"],
                    "configuration": config["name"], "max_solutions": mode,
                    "counters": first[3], "native_times_seconds": times,
                    "runtime_median_seconds": statistics.median(times), **status})
    return rows


def original_split(seed, count, fraction, datasets=cal.DEFAULT_DATASETS):
    puzzles = cal.read_puzzles(datasets, count, seed)
    if any(sum(p["size"] == n for p in puzzles) != count for n in (7, 8, 9)):
        raise ValueError("Cannot reproduce requested puzzle population")
    return cal.split(puzzles, fraction, seed)


def resolve_seed(model, override=None):
    """Use an explicit CLI override or the reference model's saved seed."""
    value = override if override is not None else model.get("calibration_seed")
    if value is None:
        raise ValueError("Calibration seed missing; supply --seed explicitly")
    return int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, action="append")
    parser.add_argument("--seed", type=int, help="Override the first model\'s calibration seed")
    parser.add_argument("--population-per-size", type=int)
    parser.add_argument("--puzzles-per-size", type=int, default=100)
    parser.add_argument("--validation-fraction", type=float)
    parser.add_argument("--native-repeats", type=int, default=3)
    parser.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    parser.add_argument("--output", type=Path, default=cal.ROOT / "scratch/work_validation.json")
    args = parser.parse_args()
    if args.puzzles_per_size < 1 or args.native_repeats < 2:
        parser.error("Positive puzzle count and at least two native repeats required")
    models = {str(p): load_model(p) for p in (args.model or [DEFAULT_MODEL])}
    reference = next(iter(models.values()))[0]
    try:
        args.seed = resolve_seed(reference, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    args.population_per_size = (args.population_per_size if args.population_per_size is not None
                                else reference.get("calibration_puzzles_per_size", 6000))
    args.validation_fraction = (args.validation_fraction if args.validation_fraction is not None
                                else reference.get("calibration_validation_fraction", .25))
    train, holdout = original_split(args.seed, args.population_per_size, args.validation_fraction,
                                    tuple(reference.get("dataset_sha256") or cal.DEFAULT_DATASETS))
    for puzzle in train + holdout:
        if reference.get("dataset_sha256") and reference["dataset_sha256"].get(puzzle["dataset"]) != puzzle["dataset_sha256"]:
            raise ValueError("Dataset checksum differs from reference model")
    print(f"Validation seed: {args.seed}", flush=True)
    puzzles = [p for n in (7, 8, 9) for p in
               sorted((p for p in holdout if p["size"] == n), key=lambda p:
                      hashlib.sha256(f"{args.seed}:{p['identity']}".encode()).hexdigest())
               [:args.puzzles_per_size]]
    configs = cal.variants(puzzles, True, args.seed)
    rows = collect(puzzles, configs, args.cc, cal.DEFAULT_HARD_TIMEOUT,
                   cal.DEFAULT_CPU_LIMITS, {"7": 0, "8": 1, "9": 1}, args.native_repeats)
    scores = {name: {"sha256": digest, "all": cal.diagnostics(rows, model),
              "by_size": {str(n): cal.diagnostics([r for r in rows if r["size"] == n], model)
                          for n in (7, 8, 9)}}
              for name, (model, digest) in models.items()}
    report = {"seed": str(args.seed), "population_per_size": args.population_per_size,
              "validation_fraction": args.validation_fraction,
              "basis": "fresh_native_timings_on_seeded_calibration_holdout",
              "scores": scores, "samples": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(scores, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
