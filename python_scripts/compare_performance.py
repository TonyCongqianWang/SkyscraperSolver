#!/usr/bin/env python3
import subprocess
import time
import concurrent.futures
import math
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

BIN_BASELINE = os.path.join(ROOT_DIR, "skyscraper_solver_main")
BIN_TUNABLE = os.path.join(ROOT_DIR, "skyscraper_solver")

# Paths to datasets
PATH_S7 = os.path.join(ROOT_DIR, "benchmark_sets", "benchmarkSet7_easy500.txt")

# Size 8 calibrated files
PATH_S8_EASY = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_easy.txt")
PATH_S8_MED = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_medium.txt")
PATH_S8_HARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_hard.txt")
PATH_S8_XHARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_xhard.txt")

# Size 9 calibrated files
PATH_S9 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated.txt")
PATH_S9_HARDER = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated_harder.txt")

def resolve_binary_path(path):
    if not path:
        return path
    if os.name == 'nt' or sys.platform.startswith('win'):
        if not path.lower().endswith('.exe'):
            if os.path.exists(path + '.exe'):
                return path + '.exe'
    return path

def run_solver(binary, opt, clue, timeout=15.0, env=None):
    t_start = time.perf_counter()
    try:
        proc = subprocess.run(
            [binary] + opt.split() + [clue],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            env=env
        )
        elapsed = time.perf_counter() - t_start
        if proc.returncode != 0:
            return None, None
        
        nodes = None
        for line in proc.stdout.splitlines():
            if line.startswith("Nodes visited:"):
                nodes = int(line.split(":")[1].strip())
                break
        return elapsed, nodes
    except Exception:
        return None, None

def shifted_geo_mean(values, shift):
    if not values:
        return 0.0
    sum_ln = sum(math.log(max(0.0, float(x)) + shift) for x in values)
    return math.exp(sum_ln / len(values)) - shift

def evaluate_set(clues, opt, label, baseline_bin, tunable_bin, tuned_env=None):
    print(f"\nEvaluating {label} ({len(clues)} instances, options: '{opt}')...")
    
    # 3-Way Comparison Setup
    # 1. Baseline: Main solver without environment override logic
    # 2. Env Baseline: Overrides-enabled solver run with default/no environment variables
    # 3. Optimized: Overrides-enabled solver run with the tuned environment variables
    binaries = [
        ("Baseline", baseline_bin, None),
        ("Env Baseline", tunable_bin, None),
        ("Optimized", tunable_bin, tuned_env)
    ]
    
    results = {}
    for name, binary, env in binaries:
        times = []
        nodes = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_solver, binary, opt, clue, env=env) for clue in clues]
            for fut in futures:
                t, n = fut.result()
                if t is not None and n is not None:
                    times.append(t)
                    nodes.append(n)
                    
        tot_nodes = sum(nodes)
        tot_time = sum(times)
        sgm_nodes = shifted_geo_mean(nodes, 1000.0)
        sgm_time = shifted_geo_mean(times, 0.1)
        
        results[name] = {
            "total_nodes": tot_nodes,
            "total_time": tot_time,
            "sgm_nodes": sgm_nodes,
            "sgm_time": sgm_time,
            "count": len(nodes)
        }
        
    base = results["Baseline"]
    env_base = results["Env Baseline"]
    optz = results["Optimized"]
    
    # Diff vs Base (end-to-end including overrides overhead)
    nodes_diff_base = (optz["total_nodes"] - base["total_nodes"]) / base["total_nodes"] * 100 if base["total_nodes"] else 0
    sgm_nodes_diff_base = (optz["sgm_nodes"] - base["sgm_nodes"]) / base["sgm_nodes"] * 100 if base["sgm_nodes"] else 0
    time_diff_base = (optz["total_time"] - base["total_time"]) / base["total_time"] * 100 if base["total_time"] else 0
    sgm_time_diff_base = (optz["sgm_time"] - base["sgm_time"]) / base["sgm_time"] * 100 if base["sgm_time"] else 0
    
    # Diff vs Env Base (pure algorithmic gain, factoring out getenv queries)
    nodes_diff_env = (optz["total_nodes"] - env_base["total_nodes"]) / env_base["total_nodes"] * 100 if env_base["total_nodes"] else 0
    sgm_nodes_diff_env = (optz["sgm_nodes"] - env_base["sgm_nodes"]) / env_base["sgm_nodes"] * 100 if env_base["sgm_nodes"] else 0
    time_diff_env = (optz["total_time"] - env_base["total_time"]) / env_base["total_time"] * 100 if env_base["total_time"] else 0
    sgm_time_diff_env = (optz["sgm_time"] - env_base["sgm_time"]) / env_base["sgm_time"] * 100 if env_base["sgm_time"] else 0
    
    print(f"| Metric | Baseline | Env Baseline | Optimized | Diff (vs Base) | Diff (vs Env Base) |")
    print(f"|---|---|---|---|---|---|")
    print(f"| **Total Nodes** | {base['total_nodes']:,} | {env_base['total_nodes']:,} | {optz['total_nodes']:,} | {nodes_diff_base:+.2f}% | {nodes_diff_env:+.2f}% |")
    print(f"| **SGM Nodes** | {base['sgm_nodes']:,.1f} | {env_base['sgm_nodes']:,.1f} | {optz['sgm_nodes']:,.1f} | {sgm_nodes_diff_base:+.2f}% | {sgm_nodes_diff_env:+.2f}% |")
    print(f"| **Total Time** | {base['total_time']:.3f}s | {env_base['total_time']:.3f}s | {optz['total_time']:.3f}s | {time_diff_base:+.2f}% | {time_diff_env:+.2f}% |")
    print(f"| **SGM Time** | {base['sgm_time']:.3f}s | {env_base['sgm_time']:.3f}s | {optz['sgm_time']:.3f}s | {sgm_time_diff_base:+.2f}% | {sgm_time_diff_env:+.2f}% |")

def load_tuned_env(winners_path):
    tuned_env = os.environ.copy()
    if not winners_path or not os.path.exists(winners_path):
        print(f"Warning: Winners file not found at '{winners_path}'. Running without env overrides.")
        return None
    with open(winners_path, "r") as f:
        for line in f:
            if line.startswith("#define"):
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1]
                    val = parts[2]
                    tuned_env[name] = val
    return tuned_env

def run_comparison(validation_tasks, baseline_bin, tunable_bin, tuned_env=None, title="SOLVER PERFORMANCE COMPARISON"):
    """
    Programmatic entry point to run comparisons.
    validation_tasks: list of tuples (label, options, list_of_clues)
    """
    baseline = resolve_binary_path(baseline_bin)
    tunable = resolve_binary_path(tunable_bin)
    
    print("======================================================================")
    print(f"   {title}   ".center(70))
    print("======================================================================")
    for label, options, clues in validation_tasks:
        if not clues:
            continue
        evaluate_set(clues, options, label, baseline, tunable, tuned_env)
    print("======================================================================")

def read_clues(file_path):
    if not os.path.exists(file_path):
        print(f"Error: dataset file not found at {file_path}", file=sys.stderr)
        return []
    with open(file_path, "r") as f:
        return [line.strip().strip('"') for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description="Compare performance of solver binaries.")
    parser.add_argument("-b", "--baseline", default=BIN_BASELINE, help="Path to baseline binary")
    parser.add_argument("-t", "--tunable", default=BIN_TUNABLE, help="Path to overrides-enabled tunable binary")
    parser.add_argument("-s", "--size", type=int, choices=[7, 8, 9], default=None, help="Specific size to evaluate. Defaults to all.")
    parser.add_argument("-w", "--winners", default=None, help="Path to SPSA winners text file to load env overrides from.")
    args = parser.parse_args()
    
    # Auto-resolve winners file path if not provided but size is specified
    winners_file = args.winners
    if winners_file is None and args.size is not None:
        possible_winners = os.path.join(ROOT_DIR, "scratch", f"spsa_winners_s{args.size}.txt")
        if os.path.exists(possible_winners):
            winners_file = possible_winners
    
    tuned_env = None
    if winners_file:
        print(f"Loading tuned parameters from: {winners_file}")
        tuned_env = load_tuned_env(winners_file)
        
    validation_tasks = []
    
    # 1. Size 7
    if args.size is None or args.size == 7:
        s7_clues = read_clues(PATH_S7)
        if s7_clues:
            validation_tasks.append(("Size 7 Complete Set (Single Solution)", "-s 1", s7_clues))
            validation_tasks.append(("Size 7 Complete Set (Full Enumeration)", "-s 0", s7_clues))
            
    # 2. Size 8
    if args.size is None or args.size == 8:
        s8_easy = read_clues(PATH_S8_EASY)
        s8_med = read_clues(PATH_S8_MED)
        s8_hard = read_clues(PATH_S8_HARD)
        s8_xhard = read_clues(PATH_S8_XHARD)
        
        s8_all = s8_easy + s8_med + s8_hard + s8_xhard
        s8_easy_med = s8_easy + s8_med
        
        if s8_all:
            validation_tasks.append(("Size 8 Complete Set (Single Solution)", "-s 1", s8_all))
        if s8_easy_med:
            validation_tasks.append(("Size 8 Easy/Medium Complete Set (Full Enumeration)", "-s 0", s8_easy_med))
            
    # 3. Size 9
    if args.size is None or args.size == 9:
        s9_calib = read_clues(PATH_S9)
        s9_harder = read_clues(PATH_S9_HARDER)
        
        if s9_calib:
            validation_tasks.append(("Size 9 Calibrated Complete Set (Single Solution)", "-s 1", s9_calib))
        if s9_harder:
            validation_tasks.append(("Size 9 Harder Calibrated Complete Set (Single Solution)", "-s 1", s9_harder))
            
    if not validation_tasks:
        print("Error: No validation sets loaded.", file=sys.stderr)
        sys.exit(1)
        
    run_comparison(validation_tasks, args.baseline, args.tunable, tuned_env)

if __name__ == "__main__":
    main()
