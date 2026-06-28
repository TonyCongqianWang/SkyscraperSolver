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
BIN_OPTIMIZED = os.path.join(ROOT_DIR, "skyscraper_solver")

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

def evaluate_set(clues, opt, label, baseline_bin, optimized_bin, extra_bin=None, tuned_env=None):
    print(f"\nEvaluating {label} ({len(clues)} instances, options: '{opt}')...")
    
    binaries = [("Baseline", baseline_bin)]
    if extra_bin:
        extra_name = os.path.splitext(os.path.basename(extra_bin))[0]
        binaries.append((extra_name, extra_bin))
    binaries.append(("Optimized", optimized_bin))
    
    results = {}
    for name, binary in binaries:
        times = []
        nodes = []
        env = tuned_env if name == "Optimized" else None
        
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
    optz = results["Optimized"]
    
    nodes_diff = (optz["total_nodes"] - base["total_nodes"]) / base["total_nodes"] * 100 if base["total_nodes"] else 0
    sgm_nodes_diff = (optz["sgm_nodes"] - base["sgm_nodes"]) / base["sgm_nodes"] * 100 if base["sgm_nodes"] else 0
    time_diff = (optz["total_time"] - base["total_time"]) / base["total_time"] * 100 if base["total_time"] else 0
    sgm_time_diff = (optz["sgm_time"] - base["sgm_time"]) / base["sgm_time"] * 100 if base["sgm_time"] else 0
    
    if extra_bin:
        extra_name = binaries[1][0]
        ext_res = results[extra_name]
        nodes_diff_ext = (optz["total_nodes"] - ext_res["total_nodes"]) / ext_res["total_nodes"] * 100 if ext_res["total_nodes"] else 0
        sgm_nodes_diff_ext = (optz["sgm_nodes"] - ext_res["sgm_nodes"]) / ext_res["sgm_nodes"] * 100 if ext_res["sgm_nodes"] else 0
        time_diff_ext = (optz["total_time"] - ext_res["total_time"]) / ext_res["total_time"] * 100 if ext_res["total_time"] else 0
        sgm_time_diff_ext = (optz["sgm_time"] - ext_res["sgm_time"]) / ext_res["sgm_time"] * 100 if ext_res["sgm_time"] else 0
        
        print(f"| Metric | Baseline | {extra_name} | Optimized | Diff (vs Base) | Diff (vs {extra_name}) |")
        print(f"|---|---|---|---|---|---|")
        print(f"| **Total Nodes** | {base['total_nodes']:,} | {ext_res['total_nodes']:,} | {optz['total_nodes']:,} | {nodes_diff:+.2f}% | {nodes_diff_ext:+.2f}% |")
        print(f"| **SGM Nodes** | {base['sgm_nodes']:,.1f} | {ext_res['sgm_nodes']:,.1f} | {optz['sgm_nodes']:,.1f} | {sgm_nodes_diff:+.2f}% | {sgm_nodes_diff_ext:+.2f}% |")
        print(f"| **Total Time** | {base['total_time']:.3f}s | {ext_res['total_time']:.3f}s | {optz['total_time']:.3f}s | {time_diff:+.2f}% | {time_diff_ext:+.2f}% |")
        print(f"| **SGM Time** | {base['sgm_time']:.3f}s | {ext_res['sgm_time']:.3f}s | {optz['sgm_time']:.3f}s | {sgm_time_diff:+.2f}% | {sgm_time_diff_ext:+.2f}% |")
    else:
        print(f"| Metric | Baseline | Optimized | Difference |")
        print(f"|---|---|---|---|")
        print(f"| **Total Nodes** | {base['total_nodes']:,} | {optz['total_nodes']:,} | {nodes_diff:+.2f}% |")
        print(f"| **SGM Nodes** | {base['sgm_nodes']:,.1f} | {optz['sgm_nodes']:,.1f} | {sgm_nodes_diff:+.2f}% |")
        print(f"| **Total Time** | {base['total_time']:.3f}s | {optz['total_time']:.3f}s | {time_diff:+.2f}% |")
        print(f"| **SGM Time** | {base['sgm_time']:.3f}s | {optz['sgm_time']:.3f}s | {sgm_time_diff:+.2f}% |")

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

def run_comparison(validation_tasks, baseline_bin, optimized_bin, extra_bin=None, tuned_env=None):
    """
    Programmatic entry point to run comparisons.
    validation_tasks: list of tuples (label, options, list_of_clues)
    """
    baseline = resolve_binary_path(baseline_bin)
    optimized = resolve_binary_path(optimized_bin)
    extra = resolve_binary_path(extra_bin) if extra_bin else None
    
    print("======================================================================")
    print("                      SOLVER PERFORMANCE COMPARISON                   ")
    print("======================================================================")
    for label, options, clues in validation_tasks:
        if not clues:
            continue
        evaluate_set(clues, options, label, baseline, optimized, extra, tuned_env)
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
    parser.add_argument("-o", "--optimized", default=BIN_OPTIMIZED, help="Path to optimized binary")
    parser.add_argument("-e", "--extra", default=None, help="Path to an optional third stable binary")
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
        
    run_comparison(validation_tasks, args.baseline, args.optimized, args.extra, tuned_env)

if __name__ == "__main__":
    main()
