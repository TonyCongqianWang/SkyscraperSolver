#!/usr/bin/env python3
"""Reproducible issue #72 work-counter calibration; Python standard library only."""
import argparse
import hashlib
import heapq
import json
import math
import os
from pathlib import Path
import random
import re
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from symmetry import canonize_nums
from work_collinearity import analyze_and_merge, collapse_row
from work_ranking import ranking_diagnostics
from work_model_export import export_compact_model, export_collinearity
from work_section_plausibility import parse_micro_lines, summarize_plausibility

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "v3"
DEFAULT_DATASETS = (
    "puzzle_bank/spsa_datasets/le7_train.txt",
    "puzzle_bank/spsa_datasets/size8_train.txt",
    "puzzle_bank/spsa_datasets/size9_train.txt",
)
COUNTER_RE = re.compile(r"^WORK_COUNTERS (v\d+) (.+)$", re.MULTILINE)
COUNTER_NAMES = (
    "setup_cell", "setup_cache_slot", "cache_state_copy", "cache_pair_copy",
    "cache_pair_copy_call", "cache_build_check", "compact_check", "compact_move",
    "transition_compare", "transition_shift", "line_copy", "line_score",
    "line_score_value", "line_compare", "line_shift", "base_score",
    "lookahead_blend", "propagate_dp_update", "dp_init_call",
    "dp_init_write", "index_copy_call", "index_copy_pair",
    "gac_check", "assignment", "domain_invalidation",
    "node_copy", "lookahead_scan", "solution_copy", "rollback",
    "rescore_scan", "resume_scan", "rel_entropy_value", "domain_scan",
)
PARAMETER_GROUPS = {
    "le7": ("g_sel_compact_period_le7", "g_sel_rescore_period_le7",
            "g_sel_blend_period_le7", "g_sel_sort_period_le7",
            "g_sel_line_sort_period_le7", "g_lookahead_entropy_weight_le7"),
    "s8": ("g_sel_compact_period_s8", "g_sel_rescore_period_s8",
           "g_sel_blend_period_s8", "g_sel_sort_period_s8",
           "g_sel_line_sort_period_s8", "g_lookahead_entropy_weight_s8"),
    "s9": ("g_sel_compact_period_s9", "g_sel_rescore_period_s9",
           "g_sel_blend_period_s9", "g_sel_sort_period_s9",
           "g_sel_line_sort_period_s9", "g_lookahead_entropy_weight_s9"),
}
PARAM_FILES = {"g_sel_": "params_cache_period.c",
               "g_lookahead_entropy_weight_": "params_math.c"}


def read_puzzles(paths, limit, seed=72):
    """Select deterministic, symmetry-distinct puzzles from each size.

    Sample across entire SPSA training files, rather than taking the first
    128 lines (SPSA datasets may be organized into difficulty blocks).
    A bounded hash-priority reservoir keeps at most `limit` per size.
    """
    if limit < 1:
        raise ValueError("puzzles-per-size must be positive")
    selected = {7: [], 8: [], 9: []}
    seen = set()
    serial = 0
    for path in paths:
        source = Path(path)
        if not source.is_absolute():
            source = ROOT / source
        if not source.is_file():
            raise ValueError(f"Dataset not found: {source}")
        raw_bytes = source.read_bytes()
        sha = hashlib.sha256(raw_bytes).hexdigest()
        for index, raw in enumerate(raw_bytes.decode("utf-8").splitlines(), 1):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            parts = re.findall(r'"([^"]+)"', raw)
            clue = parts[0] if parts else raw.strip()
            tokens = clue.split()
            n = len(tokens) // 4
            if len(tokens) != 4 * n or n < 5 or n > 9:
                raise ValueError(f"Invalid size-5..9 puzzle at {source}:{index}")
            # SPSA le7 training is a mixture of sizes 5, 6, and 7.
            if n < 7:
                continue
            grid = parts[1] if len(parts) > 1 else None
            if grid is not None and len(grid.split()) != n * n:
                raise ValueError(f"Invalid grid at {source}:{index}")
            identity = (n, canonize_nums(tuple(map(int, tokens))), grid)
            if identity in seen:
                continue
            seen.add(identity)
            identity_hash = hashlib.sha256(repr(identity).encode("utf-8")).hexdigest()
            priority = int(hashlib.sha256(
                f"{seed}:{identity_hash}".encode("utf-8")).hexdigest(), 16)
            serial += 1
            puzzle = {
                "dataset": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
                "dataset_sha256": sha,
                "line": index, "size": n, "clue": clue, "grid": grid,
                "identity": identity_hash,
            }
            candidate = (-priority, serial, puzzle)
            heap = selected[n]
            if len(heap) < limit:
                heapq.heappush(heap, candidate)
            elif candidate[0] > heap[0][0]:
                heapq.heapreplace(heap, candidate)
    puzzles = []
    for n in (7, 8, 9):
        puzzles.extend(item[2] for item in sorted(selected[n], reverse=True))
    if not puzzles:
        raise ValueError("No puzzles in input")
    return puzzles


def puzzle_mode(puzzle, max_solutions_override):
    """0 = full enumeration (size 7 default), 1 = first solution."""
    if max_solutions_override is not None:
        return max_solutions_override
    return 0 if puzzle["size"] == 7 else 1


def applicable(variant, puzzle):
    """Skip runs for parameters belonging to another size."""
    parameters = variant["parameters"]
    if not parameters:
        return True
    name = next(iter(parameters))
    group = "le7" if puzzle["size"] <= 7 else "s" + str(puzzle["size"])
    return name in PARAMETER_GROUPS[group]


def variants(puzzles, perturb):
    groups = sorted({"le7" if p["size"] <= 7 else "s" + str(p["size"]) for p in puzzles})
    options = [{"name": "baseline", "parameters": {}}]
    if perturb:
        # One-at-a-time changes avoid confounded counter costs.
        for group in groups:
            for name in PARAMETER_GROUPS[group]:
                for factor in (0.5, 1.5):
                    options.append({"name": f"{name}_x{factor}", "parameters": {name: factor}})
    return options


def replace_parameter(text, name, factor):
    pattern = re.compile(r"(?m)^(\s*double\s+" + re.escape(name)
                         + r"\s*=\s*)([-+0-9.eE]+)(\s*;)")
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Missing parameter: {name}")
    current = float(match.group(2))
    value = max(0.0, current * factor)
    # Zero parameters receive a small, explicit nonzero perturbation.
    if current == 0.0:
        value = 0.1 if factor < 1.0 else 1.0
    return text[:match.start(2)] + format(value, ".17g") + text[match.end(2):]


def build(tempdir, variant, instrument, cc, flags):
    suffix = "_micro" if "-DWORK_MICRO_TIMING" in flags else (
        "_instrumented" if instrument else "_native")
    binary = tempdir / (variant["name"] + suffix)
    sources = sorted((ROOT / "src").glob("*.c"))
    modified = {}
    for prefix, filename in PARAM_FILES.items():
        parameters = {k: v for k, v in variant["parameters"].items() if k.startswith(prefix)}
        if parameters:
            text = (ROOT / "src" / filename).read_text(encoding="utf-8")
            for name, factor in parameters.items():
                text = replace_parameter(text, name, factor)
            path = tempdir / (variant["name"] + "_" + filename)
            path.write_text(text, encoding="utf-8")
            modified[filename] = path
    commands = [str(modified.get(s.name, s)) for s in sources]
    cmd = [cc, "-Wall", "-Wextra", "-Werror", "-O2", "-flto", "-I", str(ROOT / "src")]
    if instrument:
        cmd += ["-DWORK_INSTRUMENTED"]
    cmd += flags + commands + ["-o", str(binary)]
    subprocess.run(cmd, check=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return binary, cmd


def execute(binary, puzzle, max_solutions, timeout, include_micro=False):
    argv = [str(binary), "-s", str(max_solutions), puzzle["clue"]]
    if puzzle["grid"]:
        argv.append(puzzle["grid"])
    start = time.perf_counter_ns()
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    elapsed = (time.perf_counter_ns() - start) / 1e9
    if p.returncode:
        raise RuntimeError(f"{argv[0]} failed ({p.returncode}): {p.stderr[:500]}")
    def number(key):
        m = re.search(r"(?m)^" + re.escape(key) + r":\s*(\d+)\s*$", p.stdout)
        return int(m.group(1)) if m else None
    match = COUNTER_RE.search(p.stdout)
    counters = None
    if match:
        if match.group(1) != SCHEMA:
            raise RuntimeError(f"Unexpected counter schema {match.group(1)}")
        pairs = dict(part.split("=", 1) for part in match.group(2).split())
        if set(pairs) != set(COUNTER_NAMES) | {"solutions", "nodes"}:
            raise RuntimeError("Incomplete counter schema")
        counters = {k: int(pairs[k]) for k in COUNTER_NAMES}
        solutions, nodes = int(pairs["solutions"]), int(pairs["nodes"])
    else:
        solutions, nodes = number("Solutions found"), number("Nodes visited")
    if solutions is None or nodes is None:
        raise RuntimeError("Unable to parse solver results")
    result = (elapsed, solutions, nodes, counters)
    if include_micro:
        return result + (parse_micro_lines(p.stdout.splitlines(), COUNTER_NAMES),)
    return result


def fit_nonnegative(samples, names, max_iterations=4000, ridge_alpha=0.0,
                    contrast_weight=0.0):
    """Nonnegative ridge regression on RMS-scaled counters.

    Minimize MSE + contrast_weight * within-puzzle centered MSE
    + ridge_alpha * sum(scaled_weight**2). The intercept is nonnegative
    and unregularized. All scaling is learned on the fit rows only.
    """
    if not samples:
        raise ValueError("Cannot fit empty training rows")
    if not math.isfinite(ridge_alpha) or ridge_alpha < 0:
        raise ValueError("ridge_alpha must be a finite nonnegative number")
    if not math.isfinite(contrast_weight) or contrast_weight < 0:
        raise ValueError("contrast_weight must be a finite nonnegative number")
    names = list(names)
    targets = [float(s["runtime_median_seconds"]) for s in samples]
    count = len(samples)
    scales = [
        math.sqrt(sum(float(s["counters"][n]) ** 2
                      for s in samples) / count) or 1.0
        for n in names
    ]
    x = [[float(s["counters"][n]) / scales[j]
          for j, n in enumerate(names)] + [1.0]
         for s in samples]
    dimension = len(names) + 1
    gram = [[0.0] * dimension for _ in range(dimension)]
    rhs = [0.0] * dimension
    for row, target in zip(x, targets):
        for j, value in enumerate(row):
            rhs[j] += value * target
            for k in range(j + 1):
                gram[j][k] += value * row[k]
    if contrast_weight:
        # Mean-center observations within each puzzle identity to make
        # small configuration-to-configuration differences matter.
        groups = {}
        for row, sample, target in zip(x, samples, targets):
            key = sample.get("identity",
                             (sample.get("dataset"), sample.get("line"),
                              id(sample)))
            groups.setdefault(key, []).append((row, target))
        for group in groups.values():
            length = len(group)
            center_x = [sum(entry[0][j] for entry in group) / length
                        for j in range(dimension)]
            center_y = sum(entry[1] for entry in group) / length
            for entry, target in group:
                centered = [entry[j] - center_x[j] for j in range(dimension)]
                for j, value in enumerate(centered):
                    rhs[j] += contrast_weight * value * (target - center_y)
                    for k in range(j + 1):
                        gram[j][k] += contrast_weight * value * centered[k]
    for j in range(dimension):
        for k in range(j):
            gram[k][j] = gram[j][k]
    # Sum-of-squares form of a mean-squared-error penalty. Do not penalize b.
    for j in range(len(names)):
        gram[j][j] += count * ridge_alpha
    coeff = [0.0] * dimension
    coeff[-1] = max(0.0, min(targets))
    for iteration in range(max_iterations):
        change = 0.0
        for j in range(dimension):
            if gram[j][j] <= 1e-30:
                continue
            gradient = rhs[j] - sum(gram[j][k] * coeff[k]
                                    for k in range(dimension))
            new = max(0.0, coeff[j] + gradient / gram[j][j])
            change = max(change, abs(new - coeff[j]))
            coeff[j] = new
        if change < 1e-12:
            break
    return {"intercept_seconds": coeff[-1],
            "seconds_per_count": {name: coeff[j] / scales[j]
                                  for j, name in enumerate(names)},
            "ridge_alpha": ridge_alpha,
            "contrast_weight": contrast_weight,
            "feature_scale": "root_mean_square_of_training_count",
            "objective": "MSE + contrast_weight * centered_puzzle_MSE + ridge_alpha * sum(scaled_coefficients^2)",
            "iterations": iteration + 1}


def fit_with_merging(train, correlation_threshold, dependency_tolerance,
                     ridge_alpha=0.0, contrast_weight=0.0):
    """Determine feature groups using training data only, then NNLS fit."""
    analysis = analyze_and_merge(
        train, COUNTER_NAMES, correlation_threshold, dependency_tolerance)
    groups = analysis["groups"]
    collapsed = [dict(collapse_row(row, groups),
                      identity=row.get("identity", (row.get("dataset"), row.get("line"))))
                 for row in train]
    result = fit_nonnegative(collapsed, [g["name"] for g in groups],
                             ridge_alpha=ridge_alpha,
                             contrast_weight=contrast_weight)
    result["collinearity"] = analysis
    return result


def predict(row, model):
    groups = model.get("collinearity", {}).get("groups")
    if groups is None:
        counts = row["counters"]
    else:
        counts = collapse_row(row, groups)["counters"]
    return model["intercept_seconds"] + sum(
        counts[name] * weight
        for name, weight in model["seconds_per_count"].items())


def agreement(rows, pooled, sized):
    if not rows:
        return {"samples": 0}
    a = [predict(r, pooled) for r in rows]
    b = [predict(r, sized) for r in rows]
    return {
        "samples": len(rows),
        "mean_absolute_prediction_difference_seconds":
            statistics.mean(abs(x - y) for x, y in zip(a, b)),
        "mean_signed_difference_seconds":
            statistics.mean(x - y for x, y in zip(a, b)),
        "pooled_mae_seconds": diagnostics(rows, pooled)["mae_seconds"],
        "size_mae_seconds": diagnostics(rows, sized)["mae_seconds"],
    }


def diagnostics(rows, model, noise_z=2.0, min_delta_seconds=5e-5):
    if not rows:
        return {"samples": 0}
    errors = [predict(r, model) - r["runtime_median_seconds"] for r in rows]
    mae = statistics.mean(abs(e) for e in errors)
    ys = [r["runtime_median_seconds"] for r in rows]
    mean = statistics.mean(ys)
    ss_tot = sum((y - mean) ** 2 for y in ys)
    r2 = 1.0 - sum(e * e for e in errors) / ss_tot if ss_tot else None
    ranking = ranking_diagnostics(
        rows, lambda row: predict(row, model),
        noise_z=noise_z, min_delta_seconds=min_delta_seconds)
    return {"samples": len(rows), "mae_seconds": mae, "r2": r2, **ranking}


def split(rows, validation_fraction, seed):
    """Split symmetry-unique puzzle IDs separately in each size stratum."""
    rng = random.Random(seed)
    validation = set()
    for size in sorted({r["size"] for r in rows}):
        keys = sorted({r.get("identity", (r["dataset"], r["line"]))
                       for r in rows if r["size"] == size}, key=str)
        rng.shuffle(keys)
        n = min(len(keys) - 1, max(1, round(len(keys) * validation_fraction)))
        if len(keys) > 1:
            validation.update((size, key) for key in keys[:n])
    def in_holdout(row):
        return (row["size"], row.get("identity", (row["dataset"], row["line"]))) in validation
    return ([r for r in rows if not in_holdout(r)],
            [r for r in rows if in_holdout(r)])


def choose_regularization(train, correlation_threshold,
                          dependency_tolerance, ridge_grid, contrast_grid,
                          seed=72, noise_z=2.0, min_delta_seconds=5e-5):
    """Select hyperparameters on an inner puzzle-level holdout ONLY.

    Feature collinearity groups are learned on inner-training observations.
    The outer calibration validation set is never used for selection.
    """
    inner_train, inner_val = split(train, 0.2, seed + 1009)
    if not inner_train or not inner_val:
        return {"ridge_alpha": 0.0, "contrast_weight": 0.0,
                "reason": "insufficient_inner_puzzles", "candidates": []}
    analysis = analyze_and_merge(inner_train, COUNTER_NAMES,
                                 correlation_threshold, dependency_tolerance)
    groups = analysis["groups"]
    reduced = [dict(collapse_row(row, groups),
                    identity=row.get("identity",
                                     (row.get("dataset"), row.get("line"))))
               for row in inner_train]
    names = [group["name"] for group in groups]
    candidates = []
    best = None
    best_score = None
    for ridge_alpha in ridge_grid:
        for contrast_weight in contrast_grid:
            model = fit_nonnegative(
                reduced, names, ridge_alpha=ridge_alpha,
                contrast_weight=contrast_weight)
            model["collinearity"] = analysis
            metrics = diagnostics(
                inner_val, model, noise_z, min_delta_seconds)
            clear_pairs = metrics.get("clear_ranking_pairs", 0)
            all_pairs = metrics.get("ranking_pairs", 0)
            enough_clear = clear_pairs >= max(20, all_pairs // 10)
            # Compare robust rankings if measurable; otherwise compare
            # centered errors rather than global R2 between puzzles.
            score = ((metrics["clear_ranking_accuracy"] or 0.0)
                     if enough_clear else
                     -(metrics["within_puzzle_mae_seconds"] or 0.0))
            tie = -metrics["within_puzzle_mae_seconds"] if (
                metrics["within_puzzle_mae_seconds"] is not None) else 0.0
            preference = (score, tie, -metrics["mae_seconds"],
                          -ridge_alpha, -contrast_weight)
            item = {
                "ridge_alpha": ridge_alpha,
                "contrast_weight": contrast_weight,
                "selection_metric": "clear_ranking_accuracy"
                    if enough_clear else "negative_within_puzzle_mae",
                "selection_score": score,
                "inner_validation": metrics,
            }
            candidates.append(item)
            if best_score is None or preference > best_score:
                best_score = preference
                best = item
    return {
        "ridge_alpha": best["ridge_alpha"],
        "contrast_weight": best["contrast_weight"],
        "reason": best["selection_metric"],
        "inner_training_samples": len(inner_train),
        "inner_validation_samples": len(inner_val),
        "candidates": candidates,
    }


def fit_four_models(train, validation, correlation_threshold,
                    dependency_tolerance, ridge_grid=(0.0, 1e-6, 1e-4, 1e-2),
                    contrast_grid=(0.0, 1.0, 4.0, 16.0),
                    seed=72, noise_z=2.0, min_delta_seconds=5e-5):
    """Fit size 7/8/9 independently and a pooled model; compare predictions."""
    fits = {}
    for name, size in (("size7", 7), ("size8", 8), ("size9", 9),
                       ("all", None)):
        training = [r for r in train if size is None or r["size"] == size]
        holdout = [r for r in validation if size is None or r["size"] == size]
        if not training:
            fits[name] = {"status": "unavailable", "reason": "no training observations"}
            continue
        chosen = choose_regularization(
            training, correlation_threshold, dependency_tolerance,
            ridge_grid, contrast_grid, seed, noise_z, min_delta_seconds)
        model = fit_with_merging(
            training, correlation_threshold, dependency_tolerance,
            ridge_alpha=chosen["ridge_alpha"],
            contrast_weight=chosen["contrast_weight"])
        baseline = (model if not chosen["ridge_alpha"]
                    and not chosen["contrast_weight"] else
                    fit_with_merging(training, correlation_threshold,
                                     dependency_tolerance))
        fits[name] = {"status": "fitted", "coefficients": model,
                      "hyperparameter_selection": chosen,
                      "unregularized_validation":
                          diagnostics(holdout, baseline, noise_z, min_delta_seconds),
                      "train": diagnostics(training, model, noise_z, min_delta_seconds),
                      "validation": diagnostics(holdout, model, noise_z, min_delta_seconds),
                      "training_puzzles": len(set(r["identity"] for r in training)),
                      "validation_puzzles": len(set(r["identity"] for r in holdout))}
    pooled = fits["all"]
    comparisons = {}
    if pooled["status"] == "fitted":
        for size in (7, 8, 9):
            name = "size" + str(size)
            if fits[name]["status"] == "fitted":
                relevant = [r for r in validation if r["size"] == size]
                comparisons[name] = agreement(
                    relevant, pooled["coefficients"], fits[name]["coefficients"])
    return fits, comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", action="append", default=None,
                        help="Repeat for multiple benchmark files; can include size 7/8/9")
    parser.add_argument("--puzzles-per-size", "--limit-per-dataset", type=int,
                        default=512, dest="puzzles_per_size")
    parser.add_argument("--native-repeats", type=int, default=9)
    parser.add_argument("--instrumented-repeats", type=int, default=3)
    parser.add_argument("--no-section-timing", action="store_true",
                        help="Skip sampled CPU section timing and plausibility check")
    parser.add_argument("--no-micro-verify", action="store_true",
                        help="Skip independent end-of-calibration SPSA-validation micro check")
    parser.add_argument("--micro-puzzles-per-size", type=int, default=32,
                        help="Validation puzzles per size in independent micro check")
    parser.add_argument("--ridge-grid", default="0,1e-6,1e-4,1e-2",
                        help="Comma-separated nonnegative ridge penalties")
    parser.add_argument("--contrast-grid", default="0,1,4,16",
                        help="Comma-separated within-puzzle contrast weights")
    parser.add_argument("--ranking-noise-z", type=float, default=2.0)
    parser.add_argument("--ranking-min-delta-seconds", type=float, default=5e-5)
    parser.add_argument("--max-solutions", type=int, default=None,
                        help="Override default: size 7 full enumeration (0), 8/9 first solution (1)")
    parser.add_argument("--no-perturb", action="store_true",
                        help="Skip default cache-period/lookahead parameter perturbations")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--validation-fraction", type=float, default=0.25)
    parser.add_argument("--correlation-threshold", type=float, default=0.995)
    parser.add_argument("--dependency-tolerance", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=72)
    parser.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    parser.add_argument("--output", type=Path,
                        default=ROOT / "scratch" / "work_calibration.json")
    parser.add_argument("--model-output", type=Path,
                        help="Compact pooled model path (default: output.model.json)")
    parser.add_argument("--collinearity-output", type=Path,
                        help="Pooled collinearity path (default: output.collinearity.json)")
    args = parser.parse_args()
    if args.micro_puzzles_per_size < 1:
        parser.error("micro-puzzles-per-size must be >= 1")
    if (args.puzzles_per_size < 1 or args.native_repeats < 2
            or args.instrumented_repeats < 2):
        parser.error("puzzles-per-size must be >= 1 and repeats >= 2")
    if (not math.isfinite(args.ranking_noise_z) or args.ranking_noise_z < 0
            or not math.isfinite(args.ranking_min_delta_seconds)
            or args.ranking_min_delta_seconds < 0):
        parser.error("Ranking noise and minimum delta must be nonnegative")
    try:
        ridge_grid = tuple(float(x) for x in args.ridge_grid.split(","))
        contrast_grid = tuple(float(x) for x in args.contrast_grid.split(","))
        if (not ridge_grid or not contrast_grid or
                any(not math.isfinite(v) or v < 0
                    for v in ridge_grid + contrast_grid)):
            raise ValueError("Empty, negative or nonfinite hyperparameter")
    except ValueError as exc:
        parser.error(f"Invalid regularization grid: {exc}")
    if not 0 < args.validation_fraction < 1:
        parser.error("validation-fraction must be between zero and one")
    if args.max_solutions is not None and args.max_solutions < 0:
        parser.error("max-solutions cannot be negative")
    puzzles = read_puzzles(args.dataset or DEFAULT_DATASETS,
                           args.puzzles_per_size, args.seed)
    if args.dataset is None:
        for size in (7, 8, 9):
            found = sum(p["size"] == size for p in puzzles)
            if found != args.puzzles_per_size:
                raise ValueError(f"Only {found} distinct size-{size} puzzles available; "
                                 f"requested {args.puzzles_per_size}")
    variants_to_run = variants(puzzles, not args.no_perturb)
    counts = {size: sum(p["size"] == size for p in puzzles)
              for size in (7, 8, 9)}
    provenance = {
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                      capture_output=True, text=True).stdout.strip(),
        "compiler": subprocess.run([args.cc, "--version"], capture_output=True,
                                    text=True, check=True).stdout.splitlines()[0],
        "compile_flags": ["-Wall", "-Wextra", "-Werror", "-O2", "-flto"],
        "schema": SCHEMA,
        "configurations": variants_to_run,
        "datasets": sorted({(p["dataset"], p["dataset_sha256"]) for p in puzzles}),
        "native_repeats": args.native_repeats,
        "instrumented_repeats": args.instrumented_repeats,
        "section_timing": not args.no_section_timing,
        "micro_verification_enabled": not args.no_micro_verify,
        "micro_validation_puzzles_per_size": args.micro_puzzles_per_size,
        "section_timer": "sampled process CPU nanoseconds, every 64th section",
        "ridge_grid": ridge_grid,
        "contrast_grid": contrast_grid,
        "ranking_noise_z": args.ranking_noise_z,
        "ranking_min_delta_seconds": args.ranking_min_delta_seconds,
        "max_solutions_by_size": {
            str(size): puzzle_mode({"size": size}, args.max_solutions)
            for size in (7, 8, 9)},
        "puzzles_per_size": counts,
        "seed": args.seed, "validation_fraction": args.validation_fraction,
        "counter_schema": list(COUNTER_NAMES),
        "perturbations_enabled": not args.no_perturb,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    raw_path = args.output.with_suffix(".raw.jsonl")
    rows = []
    with raw_path.open("w", encoding="utf-8", buffering=1) as raw_file:
        with tempfile.TemporaryDirectory(prefix="sky_work_") as directory:
            build_dir = Path(directory)
            for variant in variants_to_run:
                selected = [p for p in puzzles if applicable(variant, p)]
                if not selected:
                    continue
                instr, instr_cmd = build(build_dir, variant, True, args.cc, [])
                native, native_cmd = build(build_dir, variant, False, args.cc, [])
                micro = None
                if not args.no_section_timing:
                    micro, micro_cmd = build(
                        build_dir, variant, True, args.cc, ["-DWORK_MICRO_TIMING"])
                print(f"Configuration: {variant['name']} ({len(selected)} puzzles)",
                      flush=True)
                for p in selected:
                    mode = puzzle_mode(p, args.max_solutions)
                    raw_runs = []
                    def record(kind, repeat, outcome):
                        elapsed, solutions, nodes, counters = outcome[:4]
                        event = {
                            "configuration": variant["name"],
                            "parameters": variant["parameters"],
                            "dataset": p["dataset"],
                            "dataset_sha256": p["dataset_sha256"],
                            "line": p["line"], "identity": p["identity"],
                            "size": p["size"], "max_solutions": mode,
                            "run_type": kind,
                            "instrumented": kind != "native",
                            "run_index": repeat, "elapsed_seconds": elapsed,
                            "solutions": solutions, "nodes": nodes,
                            "counters": counters,
                        }
                        if len(outcome) > 4:
                            event["micro_sections"] = outcome[4]
                        raw_file.write(json.dumps(event, sort_keys=True) + "\n")
                        raw_runs.append(event)
                    instrumented = []
                    for repeat in range(args.instrumented_repeats):
                        result = execute(instr, p, mode, args.timeout)
                        record("instrumented", repeat, result)
                        if instrumented and instrumented[0][1:] != result[1:]:
                            raise RuntimeError(
                                f"Nondeterministic counters: {p['dataset']}:{p['line']}")
                        instrumented.append(result)
                    first = instrumented[0]
                    times = []
                    for repeat in range(args.native_repeats):
                        result = execute(native, p, mode, args.timeout)
                        record("native", repeat, result)
                        seconds, native_sols, native_nodes, no_counts = result
                        if (native_sols, native_nodes) != first[1:3]:
                            raise RuntimeError("Instrumented and native search results differ")
                        if no_counts is not None:
                            raise RuntimeError("Native build contains counter output")
                        times.append(seconds)
                    micro_sections = []
                    if micro is not None:
                        timed = execute(micro, p, mode, args.timeout,
                                        include_micro=True)
                        if timed[1:4] != first[1:4]:
                            raise RuntimeError(
                                "Timed instrumentation changed solver results or counters")
                        record("micro", 0, timed)
                        micro_sections = timed[4]
                    rows.append({
                        "configuration": variant["name"],
                        "parameters": variant["parameters"],
                        "dataset": p["dataset"],
                        "dataset_sha256": p["dataset_sha256"],
                        "line": p["line"], "identity": p["identity"],
                        "size": p["size"], "clue": p["clue"],
                        "grid": p["grid"], "max_solutions": mode,
                        "solutions": first[1], "nodes": first[2],
                        "counters": first[3],
                        "native_times_seconds": times,
                        "instrumented_times_seconds": [r[0] for r in instrumented],
                        "micro_sections": micro_sections,
                        "runtime_median_seconds": statistics.median(times),
                        "raw_runs": raw_runs,
                    })
    train, heldout = split(rows, args.validation_fraction, args.seed)
    fits, agreement_metrics = fit_four_models(
        train, heldout, args.correlation_threshold, args.dependency_tolerance,
        ridge_grid, contrast_grid, args.seed, args.ranking_noise_z,
        args.ranking_min_delta_seconds)
    training_ids = {r["identity"] for r in train}
    for row in rows:
        row["split"] = "train" if row["identity"] in training_ids else "validation"
        row["predictions_seconds"] = {
            name: predict(row, fit["coefficients"])
            for name, fit in fits.items() if fit["status"] == "fitted"
            and (name == "all" or name == "size" + str(row["size"]))
        }
    pooled_metrics = {}
    if fits["all"]["status"] == "fitted":
        for size in (7, 8, 9):
            pooled_metrics["size" + str(size)] = diagnostics(
                [row for row in heldout if row["size"] == size],
                fits["all"]["coefficients"],
                args.ranking_noise_z, args.ranking_min_delta_seconds)
    plausibility = None
    if not args.no_section_timing and fits["all"]["status"] == "fitted":
        plausibility = {
            "train": summarize_plausibility(
                train, fits["all"]["coefficients"], COUNTER_NAMES),
            "validation": summarize_plausibility(
                heldout, fits["all"]["coefficients"], COUNTER_NAMES),
            "validation_by_size": {
                "size" + str(n): summarize_plausibility(
                    [row for row in heldout if row["size"] == n],
                    fits["all"]["coefficients"], COUNTER_NAMES)
                for n in (7, 8, 9)
            },
        }
    payload = {
        "version": 3, "provenance": provenance,
        "section_timing_plausibility": plausibility,
        "primary_fit": "all",
        "pooled_validation_by_size": pooled_metrics,
        "fits": fits, "agreement": agreement_metrics,
        "sample_counts": {
            "train": len(train), "validation": len(heldout),
            "train_by_size": {str(n): sum(r["size"] == n for r in train)
                              for n in (7, 8, 9)},
            "validation_by_size": {str(n): sum(r["size"] == n for r in heldout)
                                   for n in (7, 8, 9)},
        },
        "raw_jsonl": str(raw_path),
        "samples": rows,
        "objective": "predicted_seconds; tuning objective integration remains disabled",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    model_path = args.model_output or args.output.with_suffix(".model.json")
    collinearity_path = (args.collinearity_output
                         or args.output.with_suffix(".collinearity.json"))
    from datetime import datetime, timezone
    creation_time = datetime.now(timezone.utc).isoformat()
    export_compact_model(payload, model_path, args.output, creation_time)
    export_collinearity(payload, collinearity_path, args.output, creation_time)
    print(f"Saved pooled model to {model_path}")
    print(f"Saved pooled collinearity to {collinearity_path}")
    if not args.no_micro_verify:
        from work_micro_probe import run_verification
        micro_path = args.output.with_suffix(".micro.json")
        verified = run_verification(
            model_path, collinearity_path, micro_path,
            puzzles_per_size=args.micro_puzzles_per_size,
            seed=args.seed + 1009, cc=args.cc, timeout=args.timeout)
        print(f"Saved independent micro verification to {micro_path}")
        print(f"Micro split assessment: {verified['split_verification']}")
    print(f"Saved {len(rows)} samples to {args.output}")
    print(f"Saved each raw solver run to {raw_path}")
    print(json.dumps({
        "sample_counts": payload["sample_counts"],
        "validation": {name: fit.get("validation") for name, fit in fits.items()},
        "selected_penalties": {
            name: {"ridge_alpha": fit["coefficients"]["ridge_alpha"],
                   "contrast_weight": fit["coefficients"]["contrast_weight"]}
            for name, fit in fits.items() if fit["status"] == "fitted"},
        "agreement": agreement_metrics,
        "section_timing_plausibility": (
            plausibility["validation"] if plausibility else None),
    }, indent=2))



if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        sys.exit(f"Calibration failed: {exc}")
