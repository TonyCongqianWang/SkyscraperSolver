#!/usr/bin/env python3
import subprocess
import os
import shutil
import concurrent.futures
import time

MAX_WORKERS = 4
SIZE8_FILE = "benchmark_sets/benchmarkSet8_easy50.txt"
SIZE7_FILE = "benchmark_sets/benchmarkSet7_easy500.txt"

def load_instances(filepath):
    with open(filepath, "r") as f:
        return [line.strip().strip('"') for line in f if line.strip()]

def compile_config(sel_period, extra_period, threshold_0, linear_coeff, quad_coeff, idx):
    if os.path.exists("obj/sel_strat_routing.o"):
        os.remove("obj/sel_strat_routing.o")
    
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
    
    shutil.copy("skyscraper_solver", f"obj/skyscraper_solver_{idx}")
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

def evaluate_binary_on_set(binary, instances, options):
    total_nodes = 0
    start_time = time.time()
    for clues in instances:
        nodes = run_solver(binary, options, clues)
        if nodes is None:
            return None, None
        total_nodes += nodes
    elapsed = time.time() - start_time
    return total_nodes, elapsed

def evaluate_config(config_info, size7_instances, size8_instances):
    idx, sel_period, extra_period, threshold_0, linear_coeff, quad_coeff = config_info
    binary = f"obj/skyscraper_solver_{idx}"
    
    # Run Size 7
    s7_nodes, s7_time = evaluate_binary_on_set(binary, size7_instances, "-s 0")
    if s7_nodes is None:
        return None
        
    # Run Size 8
    s8_nodes, s8_time = evaluate_binary_on_set(binary, size8_instances, "-s 1")
    if s8_nodes is None:
        return None
        
    return {
        "idx": idx,
        "config": (sel_period, extra_period, threshold_0, linear_coeff, quad_coeff),
        "s7_nodes": s7_nodes,
        "s7_time": s7_time,
        "s8_nodes": s8_nodes,
        "s8_time": s8_time,
        "total_nodes": s7_nodes + s8_nodes,
        "total_time": s7_time + s8_time
    }

def main():
    # Grid space
    sel_periods = [2, 4, 8, 16]
    extra_periods = [8, 16, 32, 64]
    linear_coeffs = [0.0, 2.0, 4.0, 8.0, 16.0]
    quad_coeffs = [0.0, 0.5, 1.0, 2.0, 4.0]
    threshold_0 = 0
    
    print("Generating HPO configuration grid...")
    configs = []
    idx = 0
    for sel in sel_periods:
        for extra in extra_periods:
            for lin in linear_coeffs:
                for quad in quad_coeffs:
                    configs.append((idx, sel, extra, threshold_0, lin, quad))
                    idx += 1
                    
    total_configs = len(configs)
    print(f"Total configurations generated: {total_configs}")
    
    # Compile all configurations
    print("Compiling all configuration binaries...")
    start_time = time.time()
    compiled_configs = []
    for conf in configs:
        ok = compile_config(conf[1], conf[2], conf[3], conf[4], conf[5], conf[0])
        if ok:
            compiled_configs.append(conf)
            
    print(f"Compilation finished. Compiled {len(compiled_configs)}/{total_configs} configs in {time.time() - start_time:.2f}s")
    
    # Load instances
    s7_instances = load_instances(SIZE7_FILE)
    s8_instances = load_instances(SIZE8_FILE)
    
    print(f"\n--- Running Parallel HPO Sweep with {MAX_WORKERS} workers ---")
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(evaluate_config, conf, s7_instances, s8_instances): conf
            for conf in compiled_configs
        }
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                
    print(f"Sweep completed in {time.time() - start_time:.2f}s")
    
    # Cleanup binaries
    print("\nCleaning up temporary binaries...")
    for conf in configs:
        binary_path = f"obj/skyscraper_solver_{conf[0]}"
        if os.path.exists(binary_path):
            os.remove(binary_path)
    print("Cleanup completed.")
    
    # Sort and print results
    # 1. Sort by Time
    results_by_time = sorted(results, key=lambda x: x["total_time"])
    print("\n=== TOP 15 CONFIGURATIONS BY TIME ===")
    for i, res in enumerate(results_by_time[:15]):
        c = res["config"]
        print(f"{i+1:2d}. Config {res['idx']:3d} (SEL={c[0]}, EXTRA={c[1]}, TH0={c[2]}, LIN={c[3]}, QUAD={c[4]}) -> Time: {res['total_time']:.3f}s (S7: {res['s7_time']:.3f}s, S8: {res['s8_time']:.3f}s) | Nodes: {res['total_nodes']:,} (S7: {res['s7_nodes']:,}, S8: {res['s8_nodes']:,})")
        
    # 2. Sort by Nodes
    results_by_nodes = sorted(results, key=lambda x: x["total_nodes"])
    print("\n=== TOP 15 CONFIGURATIONS BY NODES VISITED ===")
    for i, res in enumerate(results_by_nodes[:15]):
        c = res["config"]
        print(f"{i+1:2d}. Config {res['idx']:3d} (SEL={c[0]}, EXTRA={c[1]}, TH0={c[2]}, LIN={c[3]}, QUAD={c[4]}) -> Nodes: {res['total_nodes']:,} (S7: {res['s7_nodes']:,}, S8: {res['s8_nodes']:,}) | Time: {res['total_time']:.3f}s (S7: {res['s7_time']:.3f}s, S8: {res['s8_time']:.3f}s)")

if __name__ == "__main__":
    main()
