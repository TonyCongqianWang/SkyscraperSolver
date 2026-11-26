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
from param_metadata import PARAM_METADATA, PARAMETER_MAPPING, get_active_param_names
from work_section_plausibility import parse_micro_lines, summarize_plausibility

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "v1"
DEFAULT_DATASETS = (
    "puzzle_bank/spsa_datasets/le7_train.txt",
    "puzzle_bank/spsa_datasets/size8_train.txt",
    "puzzle_bank/spsa_datasets/size9_train.txt",
)
COUNTER_RE = re.compile(r"^WORK_COUNTERS (v\d+) (.+)$", re.MULTILINE)
COUNTER_NAMES = (
    "setup_cell", "setup_cache_slot", "cache_state_copy", "cache_pair_copy",
    "cache_pair_copy_call", "cache_build_candidate", "compact_check", "compact_move",
    "transition_compare", "transition_shift", "line_copy", "line_score",
    "line_score_value", "line_compare", "line_shift", "base_score",
    "lookahead_blend", "propagate_dp_update", "dp_init_call",
    "dp_init_write", "index_copy_call", "index_copy_pair",
    "dp_candidate_check", "assignment", "domain_invalidation",
    "node_copy", "lookahead_scan", "solution_copy", "provisional_solution_rollback",
    "rescore_scan", "resume_scan", "rel_entropy_value", "domain_scan",
    "constraint_check_call", "constraint_check_cell",
    "constraint_check_unset_cell", "dirty_constraint_entry",
    "dirty_constraint_enqueue", "domain_invalidation_attempt",
    "cell_bound_skip", "cache_build_cell_scan", "cache_next_scan",
    "cache_resume_scan", "next_value_scan", "prune_line_scan",
    "dp_prefix_candidate_scan", "dp_suffix_candidate_scan",
    "dp_prune_value_scan",
)
CALIBRATION_PERTURB = 0.03
CALIBRATION_RADIUS = 4.0



def read_puzzles(paths, limit, seed=0):
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
    """Only run a configuration against its own sampled puzzle."""
    identity = variant.get("puzzle_identity")
    return identity is None or identity == puzzle["identity"]


def variants(puzzles, perturb, seed=0, c=CALIBRATION_PERTURB,
             radius=CALIBRATION_RADIUS):
    """One independently sampled antithetic ellipsoid pair for each puzzle."""
    from spsa_tune import get_default_theta, get_physical_params, project_constraints
    default = project_constraints(get_default_theta())
    configs = []
    for puzzle in puzzles:
        identity = puzzle["identity"]
        size = puzzle["size"]
        prefix = f"s{size}_{identity}"
        if not perturb:
            configs.append({"name": prefix + "_baseline",
                            "puzzle_identity": identity, "parameters": {}})
            continue
        active_names = get_active_param_names("all", size)
        indices = [i for i, (name, low, high, *_)
                   in enumerate(PARAM_METADATA)
                   if name in active_names and high > low]
        if not indices:
            raise ValueError(f"No active SPSA parameters for size {size}")
        rng = random.Random(f"{seed}:ellipsoid:{identity}")
        direction = [rng.gauss(0.0, 1.0) for _ in indices]
        norm = math.sqrt(sum(x * x for x in direction))
        if norm <= 0:
            raise ValueError("Failed to sample an ellipsoid direction")
        radial = rng.random() ** (1.0 / len(indices))
        # sqrt(d) maintains a roughly 4c marginal scale per coordinate.
        factor = radius * c * math.sqrt(len(indices)) * radial / norm
        for label, sign in (("plus", 1), ("minus", -1)):
            theta = list(default)
            for delta, idx in zip(direction, indices):
                scale = PARAM_METADATA[idx][5]
                theta[idx] = max(0.0, min(1.0, theta[idx] + sign * factor * scale * delta))
            physical = get_physical_params(project_constraints(theta))
            configs.append({
                "name": prefix + "_" + label,
                "puzzle_identity": identity,
                "parameters": {PARAM_METADATA[idx][0]: physical[PARAM_METADATA[idx][0]]
                               for idx in indices},
            })
    return configs


def effective_instrumented_repeats(repeats, section_timing):
    """Ensure the plain-run budget covers observations without section timing."""
    if not math.isfinite(repeats) or repeats < 0:
        raise ValueError("instrumented-repeats must be finite and nonnegative")
    return max(0.5 if section_timing else 1, repeats)


def instrumented_repeat_budget(observations, repeats):
    """Whole repeats plus a nearest-integer (half-up) fractional budget."""
    whole = int(repeats)
    return whole * observations + math.floor((repeats - whole) * observations + 0.5)


def _observation_groups(puzzles, configurations):
    by_identity = {}
    for variant in configurations:
        by_identity.setdefault(variant.get("puzzle_identity"), []).append(variant)
    for puzzle in puzzles:
        selected = (by_identity.get(puzzle["identity"], [])
                    + by_identity.get(None, []))
        yield puzzle, selected


def section_timing_schedule(puzzles, configurations, section_timing, seed):
    """Time one member of each pair; balance unpaired observations by size."""
    timed = set()
    if not section_timing:
        return timed
    singles = {}
    for puzzle, selected in _observation_groups(puzzles, configurations):
        ranked = sorted(
            (hashlib.sha256(repr((seed, "section-pair-v1", puzzle["identity"],
                                  variant["name"])).encode("utf-8")).digest(),
             _raw_run_key(variant["name"], puzzle, "micro", 0)[:3])
            for variant in selected)
        if len(ranked) == 1:
            singles.setdefault(puzzle["size"], []).append(ranked[0])
        else:
            timed.update(key for _, key in ranked[:len(ranked) // 2])
    for observations in singles.values():
        timed.update(key for _, key in sorted(observations)[:(len(observations) + 1) // 2])
    return timed


def instrumented_repeat_schedule(puzzles, configurations, repeats,
                                 section_timing, seed):
    """Cover untimed rows first, then allocate optional repeats deterministically."""
    effective = effective_instrumented_repeats(repeats, section_timing)
    timed = section_timing_schedule(puzzles, configurations, section_timing, seed)
    by_size = {}
    for puzzle, selected in _observation_groups(puzzles, configurations):
        for variant in selected:
            key = _raw_run_key(variant["name"], puzzle, "instrumented", 0)[:3]
            priority = hashlib.sha256(
                repr((seed, "instrumented-parity-v2", puzzle["identity"],
                      variant["name"])).encode("utf-8")).digest()
            by_size.setdefault(puzzle["size"], []).append((priority, key))
    schedule = {}
    for observations in by_size.values():
        whole = int(effective)
        for _, key in observations:
            schedule[key] = max(whole, int(key not in timed))
        budget = instrumented_repeat_budget(len(observations), effective)
        extra = budget - sum(schedule[key] for _, key in observations)
        # For rates below one, additional runs check timed observations first.
        eligible = [(priority, key) for priority, key in observations
                    if whole or key in timed]
        for _, key in sorted(eligible)[:max(0, extra)]:
            schedule[key] += 1
    return schedule


def calibration_workload_plan(puzzle_counts, perturb, native_repeats,
                              instrumented_repeats, section_timing):
    """Count puzzle-parameter observations separately from exact repeats."""
    puzzles = sum(puzzle_counts.values())
    per_puzzle = 2 if perturb else 1
    observations = puzzles * per_puzzle
    native = observations * native_repeats
    effective = effective_instrumented_repeats(
        instrumented_repeats, section_timing)
    instrumented = sum(instrumented_repeat_budget(count * per_puzzle, effective)
                       for count in puzzle_counts.values())
    section = (puzzles if perturb else sum((count + 1) // 2
               for count in puzzle_counts.values())) if section_timing else 0
    return {
        "puzzles_by_size": {str(size): count
                            for size, count in sorted(puzzle_counts.items())},
        "distinct_puzzles": puzzles,
        "configurations_per_puzzle": per_puzzle,
        "puzzle_configuration_evaluations": observations,
        "native_solver_executions": native,
        "instrumented_solver_executions": instrumented,
        "section_timing_solver_executions": section,
        "total_solver_executions": native + instrumented + section,
    }


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


def runtime_override_source():
    """Temporary runtime override constructor for the entire SPSA parameter set."""
    declarations, assignments, seen = [], [], set()
    for name, _, _, _, kind, _ in PARAM_METADATA:
        if name not in PARAMETER_MAPPING:
            raise ValueError(f"Missing SPSA parameter mapping: {name}")
        _, symbol, c_type = PARAMETER_MAPPING[name]
        if symbol in seen:
            raise ValueError(f"Duplicated mapped parameter: {name}")
        seen.add(symbol)
        if c_type != ("int" if kind is int else "double"):
            raise ValueError(f"C type mismatch: {name}")
        declarations.append(f"extern {c_type} {symbol};")
        conversion = "atoi" if kind is int else "atof"
        assignments.append(
            f'    value = getenv("{name}");\n'
            f'    if (value != NULL) {symbol} = {conversion}(value);')
    return ("\n#include <stdlib.h>\n" + "\n".join(declarations) +
            "\n__attribute__((constructor))\n"
            "static void calibration_runtime_overrides(void)\n{\n"
            "    const char *value;\n" + "\n".join(assignments) +
            "\n}\n")


def build(tempdir, variant, instrument, cc, flags):
    """Compile once per mode; use env to vary parameters between puzzles."""
    suffix = "_micro" if "-DWORK_MICRO_TIMING" in flags else (
        "_instrumented" if instrument else "_native")
    binary = tempdir / (variant["name"] + suffix)
    overlay = tempdir / "calibration_runtime_overrides.c"
    overlay.write_text(runtime_override_source(), encoding="utf-8")
    sources = sorted((ROOT / "src").glob("*.c"))
    cmd = [cc, "-Wall", "-Wextra", "-Werror", "-O2", "-flto",
           "-I", str(ROOT / "src")]
    if instrument:
        cmd += ["-DWORK_INSTRUMENTED"]
    cmd += flags + [str(source) for source in sources] + [
        str(overlay), "-o", str(binary)]
    subprocess.run(cmd, check=True, cwd=ROOT,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return binary, cmd



def execute(binary, puzzle, max_solutions, timeout, include_micro=False, env=None):
    argv = [str(binary), "-s", str(max_solutions), puzzle["clue"]]
    if puzzle["grid"]:
        argv.append(puzzle["grid"])
    start = time.perf_counter_ns()
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env)
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
    # Optimize in milliseconds for a better-scaled absolute stop tolerance.
    # Public predictions, fitted coefficients, and artifacts remain seconds.
    target_scale = 1000.0
    targets = [target_scale * float(s["runtime_median_seconds"])
               for s in samples]
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
    return {"intercept_seconds": coeff[-1] / target_scale,
            "seconds_per_count": {
                name: coeff[j] / (scales[j] * target_scale)
                for j, name in enumerate(names)},
            "ridge_alpha": ridge_alpha,
            "contrast_weight": contrast_weight,
            "feature_scale": "root_mean_square_of_training_count",
            "optimizer_target_unit": "milliseconds",
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


def _raw_run_key(configuration, puzzle, kind, repeat):
    """Identity of one deterministic solver invocation in the raw journal."""
    return (configuration, puzzle["dataset"], puzzle["line"], kind, repeat)


def _outcome_from_raw(event):
    result = (event["elapsed_seconds"], event["solutions"], event["nodes"],
              event["counters"])
    if event["run_type"] == "micro":
        return result + (event["micro_sections"],)
    return result


def calibration_run_plan(seed, native_repeats, instrumented_repeats,
                         section_timing):
    """Record the schedule inputs in new journal entries."""
    return {"seed": seed, "native_repeats": native_repeats,
            "instrumented_repeats": instrumented_repeats,
            "section_timing": section_timing,
            "parity_sampling": "seeded_size_stratified_hash_v2",
            "section_sampling": "one_per_antithetic_pair_v1"}


def load_completed_runs(path, puzzles, configurations, max_solutions,
                        native_repeats, instrumented_repeats,
                        section_timing, seed=0):
    """Recover completed individual invocations, including partial puzzles.

    Fail closed if a journal entry does not belong to this exact sampled
    workload. Never silently mix different seeds, parameter choices, data
    files, or counter schemas. Legacy journals need no added manifest.
    """
    by_puzzle = {(p["dataset"], p["line"]): p for p in puzzles}
    by_configuration = {v["name"]: v for v in configurations}
    schedule = instrumented_repeat_schedule(
        puzzles, configurations, instrumented_repeats, section_timing, seed)
    timed = section_timing_schedule(puzzles, configurations, section_timing, seed)
    run_plan = calibration_run_plan(
        seed, native_repeats, instrumented_repeats, section_timing)
    completed = {}
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                configuration = by_configuration[event["configuration"]]
                puzzle = by_puzzle[(event["dataset"], event["line"])]
                kind = event["run_type"]
                repeat = event["run_index"]
                key = _raw_run_key(configuration["name"], puzzle, kind, repeat)
                if "run_plan" in event and event["run_plan"] != run_plan:
                    raise ValueError("mismatched calibration run plan")
                limit = {"native": native_repeats,
                         "instrumented": schedule.get(key[:3], 0),
                         "micro": int(key[:3] in timed)}[kind]
                if (type(repeat) is not int or not 0 <= repeat < limit
                        or event["dataset_sha256"] != puzzle["dataset_sha256"]
                        or event["identity"] != puzzle["identity"]
                        or event["size"] != puzzle["size"]
                        or event["max_solutions"] != puzzle_mode(puzzle, max_solutions)
                        or event["parameters"] != configuration["parameters"]
                        or not applicable(configuration, puzzle)):
                    raise ValueError("mismatched puzzle, parameters, or run")
                counters = event["counters"]
                if kind == "native":
                    if counters is not None:
                        raise ValueError("native run has work counters")
                elif (not isinstance(counters, dict)
                      or set(counters) != set(COUNTER_NAMES)
                      or any(type(value) is not int or value < 0
                             for value in counters.values())):
                    raise ValueError("incompatible work counter schema")
                if (kind == "micro") != ("micro_sections" in event):
                    raise ValueError("incompatible section-timing record")
                if kind == "micro" and not isinstance(event["micro_sections"], list):
                    raise ValueError("malformed micro sections")
                seconds = event["elapsed_seconds"]
                if (not isinstance(seconds, (int, float))
                        or not math.isfinite(seconds) or seconds < 0
                        or any(type(event[name]) is not int or event[name] < 0
                               for name in ("solutions", "nodes"))):
                    raise ValueError("invalid solver measurement")
                if key in completed:
                    raise ValueError("duplicate solver invocation")
                completed[key] = event
            except (ValueError, TypeError, KeyError, IndexError) as exc:
                raise ValueError(
                    f"Cannot resume {path}, line {line_number}: {exc}. "
                    "Preserve the raw file; use the original seed and options."
                ) from exc
    return completed


def measure_observation(run_or_reuse, instr, native, micro,
                        scheduled_repeats, native_repeats):
    """Use the assigned counter source; extra plain runs check parity."""
    micro_sections = []
    first = None
    if micro is not None:
        timed = run_or_reuse("micro", 0, micro, include_micro=True)
        first, micro_sections = timed[:4], timed[4]
        if first[3] is None:
            raise RuntimeError("Section-timed build missing work counters")
    instrumented = []
    for repeat in range(scheduled_repeats):
        result = run_or_reuse("instrumented", repeat, instr)
        if result[3] is None:
            raise RuntimeError("Instrumented build missing work counters")
        if first is None:
            first = result
        elif result[1:4] != first[1:4]:
            raise RuntimeError("Instrumented counter parity mismatch")
        instrumented.append(result)
    if first is None:
        raise RuntimeError("No work counter source for observation")
    times = []
    for repeat in range(native_repeats):
        seconds, native_sols, native_nodes, no_counts = run_or_reuse(
            "native", repeat, native)
        if (native_sols, native_nodes) != first[1:3]:
            raise RuntimeError("Instrumented and native search results differ")
        if no_counts is not None:
            raise RuntimeError("Native build contains counter output")
        times.append(seconds)
    return first, times, instrumented, micro_sections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", action="append", default=None,
                        help="Repeat for multiple benchmark files; can include size 7/8/9")
    parser.add_argument("--puzzles-per-size", "--limit-per-dataset", type=int,
                        default=2000, dest="puzzles_per_size",
                        help="Symmetry-distinct puzzles per size (default 2000)")
    parser.add_argument("--native-repeats", type=int, default=2)
    parser.add_argument("--instrumented-repeats", type=float, default=0.5,
                        help="Plain instrumented runs per observation "
                             "(default/minimum 0.5 with paired section timing; "
                             "minimum one without section timing). Higher rates "
                             "add deterministic parity checks")
    parser.add_argument("--no-section-timing", action="store_true",
                        help="Skip sampled CPU section timing and plausibility check")
    parser.add_argument("--no-micro-verify", action="store_true",
                        help="Skip independent end-of-calibration SPSA-validation micro check")
    parser.add_argument("--micro-puzzles-per-size", type=int, default=32,
                        help="Validation puzzles per size in independent micro check")
    parser.add_argument("--micro-repeats", type=int, default=200000,
                        help="Repeated real C operations per controlled micro point")
    parser.add_argument("--micro-rounds", type=int, default=3,
                        help="Independent controlled timing rounds; must be >=3")
    parser.add_argument("--ridge-grid", default="0,1e-6,1e-4,1e-2",
                        help="Comma-separated nonnegative ridge penalties")
    parser.add_argument("--contrast-grid", default="0,1,4,16",
                        help="Comma-separated within-puzzle contrast weights")
    parser.add_argument("--ranking-noise-z", type=float, default=2.0)
    parser.add_argument("--ranking-min-delta-seconds", type=float, default=5e-5)
    parser.add_argument("--max-solutions", type=int, default=None,
                        help="Override default: size 7 full enumeration (0), 8/9 first solution (1)")
    parser.add_argument("--perturb", type=float, default=CALIBRATION_PERTURB,
                        help="SPSA-normalized perturbation c (default 0.03)")
    parser.add_argument("--perturb-radius", type=float, default=CALIBRATION_RADIUS,
                        help="Ellipsoid axis multiplier relative to c (default 4)")
    parser.add_argument("--no-perturb", action="store_true",
                        help="Skip default cache-period/lookahead parameter perturbations")
    parser.add_argument("--timeout", type=float, default=None,
                        help="Optional per-solver-run timeout in seconds; default: unlimited")
    parser.add_argument("--resume", action="store_true",
                        help="Reuse validated individual runs from the existing raw JSONL journal")
    parser.add_argument("--fresh", action="store_true",
                        help="Explicitly overwrite an existing raw journal and start over")
    parser.add_argument("--validation-fraction", type=float, default=0.25)
    parser.add_argument("--correlation-threshold", type=float, default=0.995)
    parser.add_argument("--dependency-tolerance", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=None,
                        help="Random default; pass an integer to reproduce puzzle splits and perturbations")
    parser.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    parser.add_argument("--output", type=Path,
                        default=ROOT / "scratch" / "work_calibration.json")
    parser.add_argument("--model-output", type=Path,
                        help="Compact pooled model path (default: output.model.json)")
    parser.add_argument("--collinearity-output", type=Path,
                        help="Pooled collinearity path (default: output.collinearity.json)")
    args = parser.parse_args()
    if args.resume and args.fresh:
        parser.error("--resume and --fresh cannot be combined")
    if args.resume and args.seed is None:
        parser.error("--resume requires the original --seed")
    if args.timeout is not None and (not math.isfinite(args.timeout)
                                    or args.timeout <= 0):
        parser.error("--timeout must be a positive number of seconds")
    if args.seed is None:
        args.seed = random.SystemRandom().getrandbits(64)
    print(f"Calibration seed: {args.seed}", flush=True)
    if args.micro_puzzles_per_size < 1:
        parser.error("micro-puzzles-per-size must be >= 1")
    if args.micro_repeats < 1000 or args.micro_rounds < 3:
        parser.error("micro-repeats >= 1000 and micro-rounds >= 3 required")
    if args.puzzles_per_size < 1 or args.native_repeats < 2:
        parser.error("puzzles-per-size must be >= 1 and native-repeats >= 2")
    if not math.isfinite(args.instrumented_repeats) or args.instrumented_repeats < 0:
        parser.error("instrumented-repeats must be finite and nonnegative")
    effective_repeats = effective_instrumented_repeats(
        args.instrumented_repeats, not args.no_section_timing)
    if args.instrumented_repeats < effective_repeats:
        print(f"Using {effective_repeats} plain instrumented runs per observation "
              "to ensure complete counter coverage", flush=True)
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
    if not math.isfinite(args.perturb) or args.perturb <= 0:
        parser.error("--perturb must be finite and positive")
    if not math.isfinite(args.perturb_radius) or args.perturb_radius <= 0:
        parser.error("--perturb-radius must be finite and positive")
    if not 0 < args.validation_fraction < 1:
        parser.error("validation-fraction must be between zero and one")
    if args.max_solutions is not None and args.max_solutions < 0:
        parser.error("max-solutions cannot be negative")
    puzzles = read_puzzles(args.dataset or DEFAULT_DATASETS,
                           args.puzzles_per_size, args.seed)
    counts = {size: sum(p["size"] == size for p in puzzles)
              for size in (7, 8, 9)}
    # Fail before generating parameter vectors or compiling the solver if
    # the datasets cannot supply the requested symmetry-distinct samples.
    sizes_to_check = (7, 8, 9) if args.dataset is None else (
        size for size in (7, 8, 9) if counts[size] > 0)
    for size in sizes_to_check:
        if counts[size] != args.puzzles_per_size:
            raise ValueError(
                f"Only {counts[size]} symmetry-distinct size-{size} puzzles "
                f"available; requested {args.puzzles_per_size}. "
                "Use larger datasets or explicitly reduce --puzzles-per-size; "
                "coverage is never silently reduced.")
    plan = calibration_workload_plan(
        counts, not args.no_perturb, args.native_repeats,
        args.instrumented_repeats, not args.no_section_timing)
    print(
        "Calibration workload plan (distinct puzzles vs evaluations):\n"
        f"  Puzzles by size: {plan['puzzles_by_size']}\n"
        f"  Distinct puzzles: {plan['distinct_puzzles']:,}\n"
        f"  Configurations per puzzle: {plan['configurations_per_puzzle']}\n"
        f"  Distinct puzzle-configuration evaluations: "
        f"{plan['puzzle_configuration_evaluations']:,}\n"
        f"  Native executions: {plan['native_solver_executions']:,}\n"
        f"  Instrumented executions: "
        f"{plan['instrumented_solver_executions']:,}\n"
        f"  Section-timing executions: "
        f"{plan['section_timing_solver_executions']:,}\n"
        f"  Total solver executions: {plan['total_solver_executions']:,}",
        flush=True)
    variants_to_run = variants(puzzles, not args.no_perturb, args.seed,
                               args.perturb, args.perturb_radius)
    if all("puzzle_identity" in v for v in variants_to_run):
        if len(variants_to_run) != plan["puzzle_configuration_evaluations"]:
            raise ValueError("Generated parameter configurations do not "
                             "match the preflight evaluation count")
    schedule = instrumented_repeat_schedule(
        puzzles, variants_to_run, args.instrumented_repeats,
        not args.no_section_timing, args.seed)
    timed = section_timing_schedule(
        puzzles, variants_to_run, not args.no_section_timing, args.seed)
    if (sum(schedule.values()) != plan["instrumented_solver_executions"]
            or len(timed) != plan["section_timing_solver_executions"]
            or any(not count and key not in timed for key, count in schedule.items())):
        raise ValueError("Generated instrumentation schedule does not match preflight")
    run_plan = calibration_run_plan(
        args.seed, args.native_repeats, args.instrumented_repeats,
        not args.no_section_timing)
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
        "effective_instrumented_repeats": effective_instrumented_repeats(
            args.instrumented_repeats, not args.no_section_timing),
        "parity_sampling": run_plan["parity_sampling"],
        "section_sampling": run_plan["section_sampling"],
        "counter_source": "instrumented" if args.no_section_timing else "paired_micro_and_instrumented",
        "section_timing": not args.no_section_timing,
        "micro_verification_enabled": not args.no_micro_verify,
        "solver_timeout_seconds": args.timeout,
        "resumed_from_raw": args.resume,
        "micro_validation_puzzles_per_size": args.micro_puzzles_per_size,
        "controlled_micro_repeats": args.micro_repeats,
        "controlled_micro_rounds": args.micro_rounds,
        "section_timer": "sampled process CPU nanoseconds, every 64th section",
        "ridge_grid": ridge_grid,
        "contrast_grid": contrast_grid,
        "ranking_noise_z": args.ranking_noise_z,
        "ranking_min_delta_seconds": args.ranking_min_delta_seconds,
        "max_solutions_by_size": {
            str(size): puzzle_mode({"size": size}, args.max_solutions)
            for size in (7, 8, 9)},
        "puzzles_per_size": counts,
        "workload_plan": plan,
        "seed": args.seed, "validation_fraction": args.validation_fraction,
        "sampling_strategy": "seeded_symmetry_unique_hash_priority",
        "perturbation_strategy": "one_antithetic_ellipsoid_pair_per_puzzle_all_spsa_parameters",
        "perturbation_pairs_per_puzzle": 1,
        "perturbation_c": args.perturb,
        "perturbation_radius_multiplier": args.perturb_radius,
        "runtime_parameter_overrides": True,
        "active_parameters_by_size": {
            str(size): sorted(get_active_param_names("all", size))
            for size in (7, 8, 9)},
        "counter_schema": list(COUNTER_NAMES),
        "perturbations_enabled": not args.no_perturb,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    raw_path = args.output.with_suffix(".raw.jsonl")
    if args.resume:
        if not raw_path.is_file():
            raise FileNotFoundError(f"No raw journal to resume: {raw_path}")
        completed = load_completed_runs(
            raw_path, puzzles, variants_to_run, args.max_solutions,
            args.native_repeats, args.instrumented_repeats,
            not args.no_section_timing, seed=args.seed)
        print(f"Resuming {len(completed)} completed solver runs from "
              f"{raw_path}", flush=True)
    else:
        completed = {}
        if raw_path.exists() and not args.fresh:
            raise FileExistsError(
                f"Existing calibration journal: {raw_path}. Use --resume "
                "with its original --seed to preserve completed work, or "
                "--fresh to explicitly overwrite it.")
    rows = []
    raw_mode = "a" if args.resume else ("w" if args.fresh else "x")
    by_puzzle = {}
    for variant in variants_to_run:
        by_puzzle.setdefault(variant.get("puzzle_identity"), []).append(variant)
    from spsa_tune import get_default_theta, get_physical_params, project_constraints
    defaults = get_physical_params(project_constraints(get_default_theta()))
    default_env = os.environ.copy()
    default_env.update({name: str(value) for name, value in defaults.items()})
    with raw_path.open(raw_mode, encoding="utf-8", buffering=1) as raw_file:
        with tempfile.TemporaryDirectory(prefix="sky_work_") as directory:
            build_dir = Path(directory)
            fixed = {"name": "calibration", "parameters": {}}
            instr = None
            if plan["instrumented_solver_executions"]:
                instr, instr_cmd = build(build_dir, fixed, True, args.cc, [])
            native, native_cmd = build(build_dir, fixed, False, args.cc, [])
            micro = None
            if plan["section_timing_solver_executions"]:
                micro, micro_cmd = build(
                    build_dir, fixed, True, args.cc, ["-DWORK_MICRO_TIMING"])
            for position, p in enumerate(puzzles, 1):
                selected = by_puzzle.get(p["identity"], []) + by_puzzle.get(None, [])
                if not selected:
                    raise ValueError("No configurations for selected puzzle")
                for variant in selected:
                    env = dict(default_env)
                    env.update({name: str(value)
                                for name, value in variant["parameters"].items()})
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
                            "run_plan": run_plan,
                            "instrumented": kind != "native",
                            "run_index": repeat, "elapsed_seconds": elapsed,
                            "solutions": solutions, "nodes": nodes,
                            "counters": counters,
                        }
                        if len(outcome) > 4:
                            event["micro_sections"] = outcome[4]
                        raw_file.write(json.dumps(event, sort_keys=True) + "\n")
                        raw_runs.append(event)
                    def run_or_reuse(kind, repeat, binary, include_micro=False):
                        key = _raw_run_key(variant["name"], p, kind, repeat)
                        event = completed.pop(key, None)
                        if event is not None:
                            raw_runs.append(event)
                            return _outcome_from_raw(event)
                        result = execute(binary, p, mode, args.timeout,
                                         include_micro=include_micro, env=env)
                        record(kind, repeat, result)
                        return result

                    key = _raw_run_key(variant["name"], p, "instrumented", 0)[:3]
                    observation_micro = micro if key in timed else None
                    first, times, instrumented, micro_sections = measure_observation(
                        run_or_reuse, instr, native, observation_micro, schedule[key],
                        args.native_repeats)
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
                        "counter_source": "micro" if observation_micro is not None else "instrumented",
                        "native_times_seconds": times,
                        "instrumented_times_seconds": [r[0] for r in instrumented],
                        "micro_sections": micro_sections,
                        "runtime_median_seconds": statistics.median(times),
                        "native_pair_spread_seconds": max(times) - min(times),
                        "native_pair_relative_spread": (
                            (max(times) - min(times)) / statistics.mean(times)
                            if statistics.mean(times) > 0 else None),
                        "raw_runs": raw_runs,
                    })
                if position % 64 == 0:
                    print(f"Completed {position}/{len(puzzles)} distinct puzzles",
                          flush=True)
    if completed:
        raise ValueError(f"{len(completed)} unused cached solver runs; "
                         "preserve the raw journal and verify the parameters")
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
        timed_train = [row for row in train if row["counter_source"] == "micro"]
        timed_heldout = [row for row in heldout if row["counter_source"] == "micro"]
        plausibility = {
            "train": summarize_plausibility(
                timed_train, fits["all"]["coefficients"], COUNTER_NAMES),
            "validation": summarize_plausibility(
                timed_heldout, fits["all"]["coefficients"], COUNTER_NAMES),
            "validation_by_size": {
                "size" + str(n): summarize_plausibility(
                    [row for row in timed_heldout if row["size"] == n],
                    fits["all"]["coefficients"], COUNTER_NAMES)
                for n in (7, 8, 9)
            },
        }
    # The pooled regression is complete; uncertain timing is not fatal.
    warnings = []
    def warn(message):
        warnings.append(message)
        print(f"WARNING: {message}", file=sys.stderr, flush=True)

    from work_micro_probe import controlled_microbench
    from work_micro_constraints import allocate_merged_coefficients
    try:
        controlled = controlled_microbench(
            args.cc, args.micro_repeats, args.micro_rounds)
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        warn(f"Controlled microbenchmark unavailable: {exc}")
        controlled = {
            "status": "failed", "error": str(exc),
            "rounds": 0, "raw_measurements": [], "sections": {},
            "repeats_per_point": args.micro_repeats,
            "requested_rounds": args.micro_rounds,
        }

    pooled_model = fits["all"]["coefficients"]
    timing_training = plausibility["train"] if plausibility else {"sections": {}}
    allocation = allocate_merged_coefficients(
        pooled_model, train, controlled, timing_training)
    for warning in allocation["warnings"]:
        warn(warning)

    if allocation["all_merged_groups_resolved"]:
        flat_weights = allocation["seconds_per_count"]
        allocated_model = {
            "intercept_seconds": pooled_model["intercept_seconds"],
            "seconds_per_count": {
                name: flat_weights.get(name, 0.0) for name in COUNTER_NAMES}}
        allocation["held_out_validation"] = diagnostics(
            heldout, allocated_model, args.ranking_noise_z,
            args.ranking_min_delta_seconds)
        allocation["held_out_validation_by_size"] = {
            str(n): diagnostics(
                [row for row in heldout if row["size"] == n], allocated_model,
                args.ranking_noise_z, args.ranking_min_delta_seconds)
            for n in (7, 8, 9)}
        for row in rows:
            row["predictions_seconds"]["pooled_allocated"] = (
                pooled_model["intercept_seconds"] + sum(
                    flat_weights.get(name, 0.0) * row["counters"][name]
                    for name in COUNTER_NAMES))
    else:
        allocation["held_out_validation"] = None
        allocation["held_out_validation_by_size"] = {}
        for row in rows:
            row["predictions_seconds"]["pooled_allocated"] = None
    allocation["regression_fits_changed"] = False
    payload = {
        "version": 1, "provenance": provenance,
        "status": "partial" if warnings else "complete",
        "warnings": warnings,
        "section_timing_plausibility": plausibility,
        "controlled_microbenchmark": controlled,
        "pooled_unmerging": allocation,
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
        "objective": "predicted_seconds",
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
    # Always validate independently, including when individual allocations
    # are unresolved. Use the already-fitted pooled predictor as a diagnostic
    # projection; it is not an exported replacement for missing weights.
    micro_path = args.output.with_suffix(".micro.json")
    from work_micro_probe import run_verification
    from work_model_export import pooled_validation_projection
    if args.no_micro_verify:
        micro_report = {
            "status": "skipped_by_request",
            "warnings": ["Independent micro verification disabled by --no-micro-verify"],
            "controlled_microbenchmark": controlled,
        }
    else:
        unresolved = [g["group"] for g in allocation["unresolved_groups"]]
        verification_options = {}
        if unresolved:
            verification_options = {
                "diagnostic_model": pooled_validation_projection(payload),
                "unresolved_groups": unresolved,
            }
            warn("Independent validation will use the fitted pooled regression "
                 "while unresolved per-counter cost ratios remain unverified")
        try:
            micro_report = run_verification(
                model_path, collinearity_path, micro_path,
                puzzles_per_size=args.micro_puzzles_per_size,
                seed=args.seed + 1009, cc=args.cc, timeout=args.timeout,
                controlled_result=controlled, **verification_options)
            print(f"Micro split assessment: {micro_report['split_verification']}")
        except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError,
                subprocess.TimeoutExpired) as exc:
            warn(f"Independent validation failed, retaining other results: {exc}")
            micro_report = {
                "status": "failed", "warnings": [str(exc)],
                "validation_basis": ("pooled_merged_regression_projection"
                                     if unresolved else "allocated_per_counter_model"),
                "unresolved_groups": unresolved,
                "controlled_microbenchmark": controlled,
            }
    if args.no_micro_verify or micro_report.get("status") == "failed":
        micro_path.parent.mkdir(parents=True, exist_ok=True)
        micro_path.write_text(
            json.dumps(micro_report, indent=2, sort_keys=True,
                       allow_nan=False) + "\n", encoding="utf-8")
    payload["micro_verification_status"] = micro_report.get("status", "complete")
    payload["status"] = "partial" if warnings else "complete"
    payload["warnings"] = warnings
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"Saved micro verification report to {micro_path}")
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
