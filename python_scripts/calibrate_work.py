#!/usr/bin/env python3
"""Reproducible issue #72 work-counter calibration; Python standard library only."""
import argparse
import hashlib
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

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "v1"
DEFAULT_DATASETS = (
    "benchmark_sets/benchmarkSet7_easy500.txt",
    "benchmark_sets/benchmarkSet8_easy50.txt",
    "benchmark_sets/benchmarkSet9_easy14.txt",
)
COUNTER_RE = re.compile(r"^WORK_COUNTERS (v\d+) (.+)$", re.MULTILINE)
COUNTER_NAMES = (
    "setup_cell", "setup_cache_slot", "cache_state_copy", "cache_pair_copy",
    "cache_build_check", "compact_check", "compact_move",
    "transition_compare", "transition_shift", "line_copy", "line_score",
    "line_compare", "line_shift", "base_score", "lookahead_blend",
    "propagate_dp_update", "gac_check", "assignment", "domain_invalidation",
    "node_copy", "lookahead_scan", "solution_copy", "rollback",
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


def read_puzzles(paths, limit):
    puzzles = []
    for path in paths:
        source = Path(path)
        if not source.is_absolute():
            source = ROOT / source
        if not source.is_file():
            raise ValueError(f"Dataset not found: {source}")
        lines = source.read_text(encoding="utf-8").splitlines()
        added = 0
        for index, raw in enumerate(lines, 1):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            parts = re.findall(r'"([^"]+)"', raw)
            clue = parts[0] if parts else raw.strip()
            n = len(clue.split()) // 4
            if n not in range(4, 10) or len(clue.split()) != 4 * n:
                raise ValueError(f"Invalid puzzle at {source}:{index}")
            grid = parts[1] if len(parts) > 1 else None
            if grid is not None and len(grid.split()) != n * n:
                raise ValueError(f"Invalid grid at {source}:{index}")
            puzzles.append({
                "dataset": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
                "dataset_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "line": index, "size": n, "clue": clue, "grid": grid,
            })
            added += 1
            if added == limit:
                break
    if not puzzles:
        raise ValueError("No puzzles in input")
    return puzzles


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
    binary = tempdir / (variant["name"] + ("_instrumented" if instrument else "_native"))
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


def execute(binary, puzzle, max_solutions, timeout):
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
    return elapsed, solutions, nodes, counters


def fit_nonnegative(samples, names, max_iterations=12000):
    """Scaled cyclic coordinate descent for least-squares NNLS with intercept."""
    features = [[float(s["counters"][n]) for n in names] for s in samples]
    targets = [float(s["runtime_median_seconds"]) for s in samples]
    count = len(targets)
    scales = [max((row[j] for row in features), default=0.0) or 1.0
              for j in range(len(names))]
    x = [[row[j] / scales[j] for j in range(len(names))] for row in features]
    intercept = max(0.0, min(targets))
    residuals = [t - intercept for t in targets]
    coeff = [0.0] * len(names)
    for iteration in range(max_iterations):
        max_change = 0.0
        mean_residual = sum(residuals) / count
        intercept_new = max(0.0, intercept + mean_residual)
        shift = intercept_new - intercept
        residuals = [r - shift for r in residuals]
        intercept = intercept_new
        max_change = abs(shift)
        for j in range(len(names)):
            norm = sum(row[j] * row[j] for row in x)
            if norm <= 1e-30:
                continue
            delta = sum(row[j] * r for row, r in zip(x, residuals)) / norm
            new = max(0.0, coeff[j] + delta)
            change = new - coeff[j]
            if change:
                residuals = [r - change * row[j] for row, r in zip(x, residuals)]
                coeff[j] = new
                max_change = max(max_change, abs(change))
        if max_change < 1e-12:
            break
    return {"intercept_seconds": intercept,
            "seconds_per_count": {name: coeff[j] / scales[j]
                                  for j, name in enumerate(names)},
            "iterations": iteration + 1}


def predict(row, model):
    return model["intercept_seconds"] + sum(
        row["counters"][name] * weight
        for name, weight in model["seconds_per_count"].items())


def diagnostics(rows, model):
    if not rows:
        return {"samples": 0}
    errors = [predict(r, model) - r["runtime_median_seconds"] for r in rows]
    mae = statistics.mean(abs(e) for e in errors)
    ys = [r["runtime_median_seconds"] for r in rows]
    mean = statistics.mean(ys)
    ss_tot = sum((y - mean) ** 2 for y in ys)
    r2 = 1.0 - sum(e * e for e in errors) / ss_tot if ss_tot else None
    pairs = 0
    correct = 0
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            if a["dataset"] != b["dataset"] or a["line"] != b["line"]:
                continue
            if a["configuration"] == b["configuration"]:
                continue
            actual = a["runtime_median_seconds"] - b["runtime_median_seconds"]
            estimated = predict(a, model) - predict(b, model)
            if actual == 0:
                continue
            pairs += 1
            correct += (actual * estimated > 0)
    return {"samples": len(rows), "mae_seconds": mae, "r2": r2,
            "ranking_pairs": pairs,
            "ranking_accuracy": correct / pairs if pairs else None}


def split(rows, validation_fraction, seed):
    # Hold out entire puzzle identities to avoid training on variants of a
    # validation puzzle; variants still permit ranking within each split.
    keys = sorted({(r["dataset"], r["line"]) for r in rows})
    rng = random.Random(seed)
    rng.shuffle(keys)
    n = min(len(keys) - 1, max(1, round(len(keys) * validation_fraction)))
    holdout = set(keys[:n]) if len(keys) > 1 else set()
    return ([r for r in rows if (r["dataset"], r["line"]) not in holdout],
            [r for r in rows if (r["dataset"], r["line"]) in holdout])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", action="append", default=None,
                        help="Repeat for different benchmark files")
    parser.add_argument("--limit-per-dataset", type=int, default=8)
    parser.add_argument("--native-repeats", type=int, default=3)
    parser.add_argument("--max-solutions", type=int, default=1)
    parser.add_argument("--perturb", action="store_true",
                        help="Build cache-period and lookahead-weight variants")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--validation-fraction", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=72)
    parser.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    parser.add_argument("--output", type=Path,
                        default=ROOT / "scratch" / "work_calibration.json")
    args = parser.parse_args()
    if args.limit_per_dataset < 1 or args.native_repeats < 2:
        parser.error("limit must be >= 1 and native-repeats must be >= 2")
    if not 0 < args.validation_fraction < 1:
        parser.error("validation-fraction must be between zero and one")
    puzzles = read_puzzles(args.dataset or DEFAULT_DATASETS, args.limit_per_dataset)
    variants_to_run = variants(puzzles, args.perturb)
    provenance = {
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                      capture_output=True, text=True).stdout.strip(),
        "compiler": subprocess.run([args.cc, "--version"], capture_output=True,
                                    text=True, check=True).stdout.splitlines()[0],
        "compile_flags": ["-Wall", "-Wextra", "-Werror", "-O2", "-flto"],
        "schema": SCHEMA,
        "configurations": variants_to_run,
        "datasets": sorted({(p["dataset"], p["dataset_sha256"]) for p in puzzles}),
        "native_repeats": args.native_repeats, "max_solutions": args.max_solutions,
    }
    rows = []
    with tempfile.TemporaryDirectory(prefix="sky_work_") as directory:
        build_dir = Path(directory)
        for variant in variants_to_run:
            instr, instr_cmd = build(build_dir, variant, True, args.cc, [])
            native, native_cmd = build(build_dir, variant, False, args.cc, [])
            print(f"Configuration: {variant['name']}", flush=True)
            for p in puzzles:
                _, solutions, nodes, counts = execute(instr, p, args.max_solutions, args.timeout)
                again = execute(instr, p, args.max_solutions, args.timeout)
                if (solutions, nodes, counts) != (again[1], again[2], again[3]):
                    raise RuntimeError(f"Nondeterministic counters: {p['dataset']}:{p['line']}")
                times = []
                for _ in range(args.native_repeats):
                    seconds, native_sols, native_nodes, no_counts = execute(
                        native, p, args.max_solutions, args.timeout)
                    if (native_sols, native_nodes) != (solutions, nodes):
                        raise RuntimeError("Instrumented and native search results differ")
                    if no_counts is not None:
                        raise RuntimeError("Native build contains counter output")
                    times.append(seconds)
                rows.append({
                    "configuration": variant["name"],
                    "dataset": p["dataset"], "dataset_sha256": p["dataset_sha256"],
                    "line": p["line"], "size": p["size"], "clue": p["clue"],
                    "grid": p["grid"], "max_solutions": args.max_solutions,
                    "solutions": solutions, "nodes": nodes, "counters": counts,
                    "native_times_seconds": times,
                    "runtime_median_seconds": statistics.median(times),
                })
    train, holdout = split(rows, args.validation_fraction, args.seed)
    model = fit_nonnegative(train, COUNTER_NAMES)
    groups = {"le7": lambda r: r["size"] <= 7,
              "size8": lambda r: r["size"] == 8,
              "size9": lambda r: r["size"] == 9,
              "single": lambda r: r["max_solutions"] == 1,
              "enumeration": lambda r: r["max_solutions"] != 1}
    evaluation = {"train": diagnostics(train, model),
                  "validation": diagnostics(holdout, model),
                  "validation_by_group": {k: diagnostics([r for r in holdout if pred(r)], model)
                                          for k, pred in groups.items()}}
    for row in rows:
        row["work_seconds_estimate"] = predict(row, model)
        row["split"] = "validation" if row in holdout else "train"
    payload = {"version": 1, "provenance": provenance, "coefficients": model,
               "evaluation": evaluation, "samples": rows,
               "objective": "predicted_seconds; log-shift integration is NOT enabled"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"Saved {len(rows)} rows to {args.output}")
    print(json.dumps(evaluation, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        sys.exit(f"Calibration failed: {exc}")
