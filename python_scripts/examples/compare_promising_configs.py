#!/usr/bin/env python3
import subprocess
import os
import shutil
import concurrent.futures
import time
import sys

MAX_WORKERS = 3  # To completely prevent CPU contention on the 16-core machine

SIZE7_FILE = "benchmark_sets/benchmarkSet7.txt"
SIZE8_FILE = "benchmark_sets/benchmarkSet8_subset300.txt"

CONFIGS = {
    "Config_Tuned_Min_Nodes": (2, 8, 0, 2.0, 0.5),    # SEL=2, EXTRA=8, LIN=2.0, QUAD=0.5
    "Config_Fastest":         (16, 64, 0, 4.0, 2.0),  # SEL=16, EXTRA=64, LIN=4.0, QUAD=2.0
    "Config_Promising_1":     (8, 32, 0, 4.0, 2.0),   # SEL=8, EXTRA=32, LIN=4.0, QUAD=2.0
    "Config_Promising_2":     (3, 8, 0, 8.0, 0.0),    # SEL=3, EXTRA=8, LIN=8.0, QUAD=0.0
    "Config_Promising_3":     (2, 16, 0, 4.0, 0.5),   # SEL=2, EXTRA=16, LIN=4.0, QUAD=0.5
    "Config_Baseline_Unscaled":(2, 8, 0, 0.0, 0.0),   # SEL=2, EXTRA=8, LIN=0.0, QUAD=0.0
    "Config_Original_Default": (2, 150, 0, 0.0, 0.0)  # SEL=2, EXTRA=150, LIN=0.0, QUAD=0.0 (Our baseline)
}

def load_instances(filepath):
    with open(filepath, "r") as f:
        return [line.strip().strip('"') for line in f if line.strip()]

def compile_config(name, params):
    sel_period, extra_period, threshold_0, linear_coeff, quad_coeff = params
    if os.path.exists("obj/sel_strat_routing.o"):
        os.remove("obj/sel_strat_routing.o")
    if os.path.exists("skyscraper_solver"):
        os.remove("skyscraper_solver")
    
    cflags = (
        f"-Wall -Wextra -Werror -O2 "
        f"-DG_SEL_REBUILD_PERIOD={sel_period} "
        f"-DG_SEL_EXTRA_PERIOD_DEEP={extra_period} "
        f"-DG_SEL_DEPTH_THRESHOLD_0={threshold_0} "
        f"-DG_SEL_LINEAR_COEFF={linear_coeff} "
        f"-DG_SEL_QUAD_COEFF={quad_coeff}"
    )
    
    cmd = f"make CFLAGS='{cflags}'"
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if proc.returncode != 0:
        return False
    
    shutil.copy("skyscraper_solver", f"obj/solver_conf_{name}")
    return True

def run_solver(binary, options, clues):
    cmd = [binary] + options.split() + [clues]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2.0)
        if proc.returncode != 0:
            return None
        nodes = None
        for line in proc.stdout.splitlines():
            if line.startswith("Nodes visited:"):
                nodes = int(line.split(":")[1].strip())
        return nodes
    except Exception:
        return None

def evaluate_binary_on_set(binary, instances, options, name, set_label):
    total_nodes = 0
    start_time = time.time()
    n_instances = len(instances)
    
    for idx, clues in enumerate(instances):
        nodes = run_solver(binary, options, clues)
        if nodes is None:
            return None, None
        total_nodes += nodes
        
        # Periodic progress printing so the user can check in
        if (idx + 1) % 500 == 0 or idx + 1 == n_instances:
            print(f"[{name}] Completed {idx + 1}/{n_instances} on {set_label}...")
            sys.stdout.flush()
            
    elapsed = time.time() - start_time
    return total_nodes, elapsed

def evaluate_config(name, params, s7_instances, s8_instances):
    binary = f"obj/solver_conf_{name}"
    
    print(f"[{name}] Starting evaluation on Full Size 7...")
    sys.stdout.flush()
    s7_nodes, s7_time = evaluate_binary_on_set(binary, s7_instances, "-s 0", name, "S7")
    if s7_nodes is None:
        return None
        
    print(f"[{name}] Starting evaluation on Size 8 subset 300...")
    sys.stdout.flush()
    s8_nodes, s8_time = evaluate_binary_on_set(binary, s8_instances, "-s 1", name, "S8")
    if s8_nodes is None:
        return None
        
    return {
        "name": name,
        "config": params,
        "s7_nodes": s7_nodes,
        "s7_time": s7_time,
        "s8_nodes": s8_nodes,
        "s8_time": s8_time,
        "total_nodes": s7_nodes + s8_nodes,
        "total_time": s7_time + s8_time
    }

def main():
    print("Compiling all solver configurations sequentially...")
    sys.stdout.flush()
    for name, params in CONFIGS.items():
        print(f"Compiling {name}...")
        sys.stdout.flush()
        ok = compile_config(name, params)
        if not ok:
            print(f"Failed to compile {name}!")
            sys.exit(1)
            
    print("Compilation completed. Loading instances...")
    sys.stdout.flush()
    s7_instances = load_instances(SIZE7_FILE)
    s8_instances = load_instances(SIZE8_FILE)
    
    print(f"Loaded {len(s7_instances)} Size 7 instances and {len(s8_instances)} Size 8 instances.")
    print(f"Running evaluation in parallel using {MAX_WORKERS} workers...")
    sys.stdout.flush()
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(evaluate_config, name, params, s7_instances, s8_instances): name
            for name, params in CONFIGS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            res = future.result()
            if res:
                results[name] = res
                
    # Cleanup binaries
    print("Cleaning up solver binaries...")
    sys.stdout.flush()
    for name in CONFIGS.keys():
        binary_path = f"obj/solver_conf_{name}"
        if os.path.exists(binary_path):
            os.remove(binary_path)
            
    # Print comparison table
    orig = results.get("Config_Original_Default")
    if not orig:
        print("Error: Config_Original_Default results missing!")
        sys.exit(1)
        
    orig_s7_n, orig_s7_t = orig["s7_nodes"], orig["s7_time"]
    orig_s8_n, orig_s8_t = orig["s8_nodes"], orig["s8_time"]
    
    print("\n" + "="*90)
    print(f"{'Configuration Name':<28} | {'S7 Nodes':<12} | {'S7 Time':<8} | {'S8 Nodes':<12} | {'S8 Time':<8}")
    print("-"*90)
    for name, res in results.items():
        s7_n_diff = (res["s7_nodes"] - orig_s7_n) / orig_s7_n * 100
        s7_t_diff = (res["s7_time"] - orig_s7_t) / orig_s7_t * 100
        s8_n_diff = (res["s8_nodes"] - orig_s8_n) / orig_s8_n * 100
        s8_t_diff = (res["s8_time"] - orig_s8_t) / orig_s8_t * 100
        
        print(f"{name:<28} | "
              f"{res['s7_nodes']:>7,} ({s7_n_diff:>+5.1f}%) | "
              f"{res['s7_time']:>5.2f}s ({s7_t_diff:>+5.1f}%) | "
              f"{res['s8_nodes']:>7,} ({s8_n_diff:>+5.1f}%) | "
              f"{res['s8_time']:>5.2f}s ({s8_t_diff:>+5.1f}%)")
    print("="*90)

if __name__ == "__main__":
    main()
