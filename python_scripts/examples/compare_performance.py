#!/usr/bin/env python3
import subprocess
import time
import concurrent.futures
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

BIN_BASELINE = os.path.join(ROOT_DIR, "skyscraper_solver_main.exe")
BIN_OPTIMIZED = os.path.join(ROOT_DIR, "skyscraper_solver.exe")

PATH_S7 = os.path.join(ROOT_DIR, "benchmark_sets", "benchmarkSet7_easy500.txt")
PATH_S8 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_medium.txt")
PATH_S9 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated.txt")
PATH_S9_HARDER = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated_harder.txt")

def get_symmetries(T, B, L, R):
    s1 = (T, B, L, R)
    s2 = (L[::-1], R[::-1], B, T)
    s3 = (B[::-1], T[::-1], R[::-1], L[::-1])
    s4 = (R, L, T[::-1], B[::-1])
    s5 = (T[::-1], B[::-1], R, L)
    s6 = (R[::-1], L[::-1], B[::-1], T[::-1])
    s7 = (B, T, L[::-1], R[::-1])
    s8 = (L, R, T, B)
    return [s1, s2, s3, s4, s5, s6, s7, s8]

def canonize(clue_str):
    nums = list(map(int, clue_str.split()))
    n = len(nums) // 4
    T = nums[0:n]
    B = nums[n:2*n]
    L = nums[2*n:3*n]
    R = nums[3*n:4*n]
    symmetries = get_symmetries(T, B, L, R)
    sym_lists = [s[0] + s[1] + s[2] + s[3] for s in symmetries]
    return tuple(min(sym_lists))

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

def evaluate_set(clues, opt, label, tuned_env=None):
    print(f"\nEvaluating {label} ({len(clues)} instances, options: '{opt}')...")
    
    results = {}
    for name, binary in [("Baseline", BIN_BASELINE), ("Optimized", BIN_OPTIMIZED)]:
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
        
    # Print results table
    base = results["Baseline"]
    optz = results["Optimized"]
    
    nodes_diff = (optz["total_nodes"] - base["total_nodes"]) / base["total_nodes"] * 100 if base["total_nodes"] else 0
    sgm_nodes_diff = (optz["sgm_nodes"] - base["sgm_nodes"]) / base["sgm_nodes"] * 100 if base["sgm_nodes"] else 0
    time_diff = (optz["total_time"] - base["total_time"]) / base["total_time"] * 100 if base["total_time"] else 0
    sgm_time_diff = (optz["sgm_time"] - base["sgm_time"]) / base["sgm_time"] * 100 if base["sgm_time"] else 0
    
    print(f"| Metric | Baseline | Optimized | Difference |")
    print(f"|---|---|---|---|")
    print(f"| **Total Nodes** | {base['total_nodes']:,} | {optz['total_nodes']:,} | {nodes_diff:+.2f}% |")
    print(f"| **SGM Nodes** | {base['sgm_nodes']:,.1f} | {optz['sgm_nodes']:,.1f} | {sgm_nodes_diff:+.2f}% |")
    print(f"| **Total Time** | {base['total_time']:.3f}s | {optz['total_time']:.3f}s | {time_diff:+.2f}% |")
    print(f"| **SGM Time** | {base['sgm_time']:.3f}s | {optz['sgm_time']:.3f}s | {sgm_time_diff:+.2f}% |")

def load_tuned_env():
    tuned_env = os.environ.copy()
    winners_path = os.path.join(ROOT_DIR, "scratch", "spsa_winners_mixed.txt")
    if not os.path.exists(winners_path):
        print(f"Warning: Tuned winners file not found at {winners_path}.")
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

def main():
    tuned_env = load_tuned_env()
    
    # 1. S7 Held-out Validation (last 100 instances)
    with open(PATH_S7, "r") as f:
        s7_all = [line.strip().strip('"') for line in f if line.strip()]
    s7_val = s7_all[400:]
    evaluate_set(s7_val, "-s 0", "Size 7 Held-out Validation Set (Full Enumeration)", tuned_env)
    
    # 2. S8 Held-out Validation (last 37 instances)
    with open(PATH_S8, "r") as f:
        s8_all = [line.strip().strip('"') for line in f if line.strip()]
    s8_val = s8_all[146:]
    evaluate_set(s8_val, "-s 0", "Size 8 Held-out Validation Set (Full Enumeration)", tuned_env)
    
    # 3. S9 Calibrated Validation Groups (last 2 groups)
    with open(PATH_S9, "r") as f:
        s9_raw = [line.strip().strip('"') for line in f if line.strip()]
    s9_groups = {}
    for clue in s9_raw:
        key = canonize(clue)
        if key not in s9_groups:
            s9_groups[key] = []
        s9_groups[key].append(clue)
    s9_groups = list(s9_groups.values())
    s9_val_groups = s9_groups[int(len(s9_groups)*0.8):]
    s9_val = []
    for g in s9_val_groups:
        s9_val.extend(g)
    evaluate_set(s9_val, "-s 1", "Size 9 Calibrated Validation Groups (Held-out)", tuned_env)
    
    # 4. S9 Calibrated Harder Validation Groups (use remaining 50% validation groups)
    with open(PATH_S9_HARDER, "r") as f:
        s9_harder_raw = [line.strip().strip('"') for line in f if line.strip()]
    s9_harder_groups = {}
    for clue in s9_harder_raw:
        key = canonize(clue)
        if key not in s9_harder_groups:
            s9_harder_groups[key] = []
        s9_harder_groups[key].append(clue)
    s9_harder_groups = list(s9_harder_groups.values())
    s9_harder_val_groups = s9_harder_groups[int(len(s9_harder_groups)*0.5):]
    s9_harder_val = []
    for g in s9_harder_val_groups:
        s9_harder_val.extend(g)
    evaluate_set(s9_harder_val, "-s 1", "Size 9 Harder Calibrated v2 Validation Groups (Held-out)", tuned_env)

if __name__ == "__main__":
    main()
