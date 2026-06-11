#!/usr/bin/env python3
import subprocess
import os
import shutil
import concurrent.futures
import time

MAX_WORKERS_STAGE1 = 12
MAX_WORKERS_STAGE2 = 4

SIZE7_SUBSET_FILE = "benchmark_sets/benchmarkSet7_subset100.txt"
SIZE8_SUBSET_FILE = "benchmark_sets/benchmarkSet8_subset30.txt"

SIZE7_VAL_FILE = "benchmark_sets/benchmarkSet7_easy500.txt"
SIZE8_VAL_FILE = "benchmark_sets/benchmarkSet8_easy50.txt"

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
    sel_periods = [2, 3, 4, 6, 8, 12, 16]
    extra_periods = [8, 16, 32, 64, 128]
    linear_coeffs = [0.0, 1.0, 2.0, 4.0, 8.0, 16.0]
    quad_coeffs = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
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
    
    # Load instances
    s7_sub = load_instances(SIZE7_SUBSET_FILE)
    s8_sub = load_instances(SIZE8_SUBSET_FILE)
    s7_val = load_instances(SIZE7_VAL_FILE)
    s8_val = load_instances(SIZE8_VAL_FILE)
    
    print(f"\n--- STAGE 1: Broad Node Sweep (MAX_WORKERS={MAX_WORKERS_STAGE1}) ---")
    start_time = time.time()
    
    results_stage1 = []
    batch_size = 100
    for b_idx in range(0, total_configs, batch_size):
        batch = configs[b_idx:b_idx+batch_size]
        print(f"Compiling batch {b_idx//batch_size + 1}/{(total_configs-1)//batch_size + 1}...")
        
        compiled_batch = []
        for conf in batch:
            ok = compile_config(conf[1], conf[2], conf[3], conf[4], conf[5], conf[0])
            if ok:
                compiled_batch.append(conf)
        
        print(f"Evaluating batch of {len(compiled_batch)} configs...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_STAGE1) as executor:
            futures = {
                executor.submit(evaluate_config, conf, s7_sub, s8_sub): conf
                for conf in compiled_batch
            }
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    results_stage1.append(res)
                    
        # Cleanup batch binaries
        for conf in batch:
            binary_path = f"obj/skyscraper_solver_{conf[0]}"
            if os.path.exists(binary_path):
                os.remove(binary_path)
                
    print(f"Stage 1 completed in {time.time() - start_time:.2f}s")
    print(f"Successfully evaluated {len(results_stage1)} configurations.")
    
    # Find minimum nodes in Stage 1
    min_nodes = min(res["total_nodes"] for res in results_stage1)
    print(f"Minimum nodes found in Stage 1: {min_nodes:,}")
    
    # Filter configurations: total_nodes <= min_nodes * 1.01
    # Also ensure we keep at least the top 50 configurations sorted by node count
    results_stage1_sorted = sorted(results_stage1, key=lambda x: x["total_nodes"])
    threshold = min_nodes * 1.01
    
    kept_results = [res for res in results_stage1 if res["total_nodes"] <= threshold]
    if len(kept_results) < 50:
        kept_results = results_stage1_sorted[:50]
        
    print(f"Filtered down to {len(kept_results)} configurations for Stage 2 Timing Sweep (nodes <= {int(threshold):,}).")
    
    print(f"\n--- STAGE 2: Precise Timing Sweep on Validation Sets (MAX_WORKERS={MAX_WORKERS_STAGE2}) ---")
    start_time_stage2 = time.time()
    
    # Compile all kept configurations sequentially
    print(f"Compiling {len(kept_results)} binaries for Stage 2...")
    compiled_stage2 = []
    for res_s1 in kept_results:
        conf = res_s1["config"]
        idx = res_s1["idx"]
        ok = compile_config(conf[0], conf[1], conf[2], conf[3], conf[4], idx)
        if ok:
            compiled_stage2.append(res_s1)
            
    print(f"Evaluating {len(compiled_stage2)} configurations in parallel (MAX_WORKERS={MAX_WORKERS_STAGE2})...")
    results_stage2 = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_STAGE2) as executor:
        futures = {
            executor.submit(
                evaluate_config,
                (conf_info["idx"], conf_info["config"][0], conf_info["config"][1], conf_info["config"][2], conf_info["config"][3], conf_info["config"][4]),
                s7_val, s8_val
            ): conf_info
            for conf_info in compiled_stage2
        }
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results_stage2.append(res)
                
    # Cleanup Stage 2 binaries
    for res_s1 in compiled_stage2:
        binary_path = f"obj/skyscraper_solver_{res_s1['idx']}"
        if os.path.exists(binary_path):
            os.remove(binary_path)
            
    print(f"Stage 2 completed in {time.time() - start_time_stage2:.2f}s")
    
    # Sort and print results
    # 1. Sort by Time
    results_by_time = sorted(results_stage2, key=lambda x: x["total_time"])
    print("\n=== TOP 20 CONFIGURATIONS BY TIME ===")
    for i, res in enumerate(results_by_time[:20]):
        c = res["config"]
        print(f"{i+1:2d}. Config {res['idx']:3d} (SEL={c[0]}, EXTRA={c[1]}, LIN={c[3]}, QUAD={c[4]}) -> Time: {res['total_time']:.3f}s (S7: {res['s7_time']:.3f}s, S8: {res['s8_time']:.3f}s) | Nodes: {res['total_nodes']:,} (S7: {res['s7_nodes']:,}, S8: {res['s8_nodes']:,})")
        
    # 2. Sort by Nodes
    results_by_nodes = sorted(results_stage2, key=lambda x: x["total_nodes"])
    print("\n=== TOP 20 CONFIGURATIONS BY NODES VISITED ===")
    for i, res in enumerate(results_by_nodes[:20]):
        c = res["config"]
        print(f"{i+1:2d}. Config {res['idx']:3d} (SEL={c[0]}, EXTRA={c[1]}, LIN={c[3]}, QUAD={c[4]}) -> Nodes: {res['total_nodes']:,} (S7: {res['s7_nodes']:,}, S8: {res['s8_nodes']:,}) | Time: {res['total_time']:.3f}s (S7: {res['s7_time']:.3f}s, S8: {res['s8_time']:.3f}s)")

if __name__ == "__main__":
    main()
