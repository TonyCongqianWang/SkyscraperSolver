import os
import re
import sys
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_benchmark_file(filepath):
    results = []
    if not os.path.exists(filepath):
        return results
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    runs = content.split("Command: ")
    for run in runs[1:]:
        lines = run.strip().split('\n')
        command = lines[0].strip()
        
        sols_found = None
        nodes_visited = None
        elapsed = None
        
        for line in lines:
            if "Solutions found:" in line:
                sols_found = int(line.split("Solutions found:")[1].strip())
            elif "Nodes visited:" in line:
                nodes_visited = int(line.split("Nodes visited:")[1].strip())
            elif "Elapsed:" in line:
                elapsed_str = line.split("Elapsed:")[1].strip()
                parts = elapsed_str.split(":")
                if len(parts) == 3:
                    h, m, s = parts
                    elapsed = float(h)*3600 + float(m)*60 + float(s)
                elif len(parts) == 2:
                    m, s = parts
                    elapsed = float(m)*60 + float(s)
                else:
                    elapsed = float(parts[0])
        
        if sols_found is not None and nodes_visited is not None and elapsed is not None:
            results.append({
                "command": command,
                "solutions": sols_found,
                "nodes": nodes_visited,
                "time": elapsed
            })
    return results

def cleanup_worker_files(pruning_c, exe, out):
    if os.path.exists(pruning_c):
        try: os.remove(pruning_c)
        except: pass
    if os.path.exists(exe):
        try: os.remove(exe)
        except: pass
    if os.path.exists(out):
        try: os.remove(out)
        except: pass

def evaluate_config(worker_id, shallow, deep, reiterate_threshold, workspace, subset_file, base_c_files):
    src_dir = os.path.join(workspace, "src")
    orig_pruning_c = os.path.join(src_dir, "node_pruning.c")
    worker_pruning_c = os.path.join(src_dir, f"node_pruning_worker_{worker_id}.c")
    
    # Executable suffix for cross-platform compatibility
    exe_suffix = ".exe" if os.name == 'nt' else ""
    worker_exe = os.path.join(workspace, f"skyscraper_solver_worker_{worker_id}{exe_suffix}")
    worker_out = os.path.join(workspace, f"benchmark_worker_{worker_id}.txt")
    
    # Read original node_pruning.c
    try:
        with open(orig_pruning_c, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"[Worker {worker_id}] Error reading original file: {e}")
        return None
        
    # Replace constants
    content = re.sub(
        r"const t_prune_prog\s+g_prune_period_shallow\s*=\s*\d+;",
        f"const t_prune_prog\tg_prune_period_shallow = {shallow};",
        content
    )
    content = re.sub(
        r"const t_prune_prog\s+g_prune_extra_period_deep\s*=\s*\d+;",
        f"const t_prune_prog\tg_prune_extra_period_deep = {deep};",
        content
    )
    content = re.sub(
        r"const t_prune_prog\s+g_prune_reiterate_threshold\s*=\s*\d+;",
        f"const t_prune_prog\tg_prune_reiterate_threshold = {reiterate_threshold};",
        content
    )
    
    # Write worker-specific C file
    try:
        with open(worker_pruning_c, 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"[Worker {worker_id}] Error writing worker file: {e}")
        cleanup_worker_files(worker_pruning_c, worker_exe, worker_out)
        return None
        
    # Combine static list of base C files with worker-specific prune file
    c_files = list(base_c_files) + [worker_pruning_c]
    
    # Compile
    cmd = ["gcc", "-Wall", "-Wextra", "-Werror", "-O2", "-o", worker_exe] + c_files
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[Worker {worker_id}] Compile error: {result.stderr}")
        cleanup_worker_files(worker_pruning_c, worker_exe, worker_out)
        return None
        
    # Clean up any existing temp output
    if os.path.exists(worker_out):
        os.remove(worker_out)
        
    # Run the benchmark dynamically using current interpreter and relative script path
    python_exe = sys.executable
    run_script = os.path.join(workspace, "python_scripts", "run_benchmark.py")
    
    run_cmd = [
        python_exe, run_script, subset_file,
        "-f", "-s 0",
        "-c", worker_exe,
        "-o", worker_out
    ]
    
    subprocess.run(run_cmd, capture_output=True)
    
    # Parse results
    run_res = parse_benchmark_file(worker_out)
    cleanup_worker_files(worker_pruning_c, worker_exe, worker_out)
    
    if len(run_res) < 50:
        print(f"[Worker {worker_id}] Warning: Run failed or was incomplete for shallow={shallow}, deep={deep}, reiterate={reiterate_threshold}")
        return None
        
    total_nodes = sum(r["nodes"] for r in run_res)
    total_time = sum(r["time"] for r in run_res)
    
    return {
        "shallow": shallow,
        "deep": deep,
        "reiterate": reiterate_threshold,
        "nodes": total_nodes,
        "time": total_time
    }

def run_tuning():
    # Dynamic workspace detection: parent of this script's folder (python_scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace = os.path.dirname(script_dir)
    src_dir = os.path.join(workspace, "src")
    
    # Executable suffix for cross-platform compatibility
    exe_suffix = ".exe" if os.name == 'nt' else ""
    
    # Clean up leftover worker files from previous crashed runs
    print("Cleaning up leftover temporary files...")
    for f in os.listdir(src_dir):
        if f.startswith("node_pruning_worker_"):
            try: os.remove(os.path.join(src_dir, f))
            except: pass
    for f in os.listdir(workspace):
        if f.startswith("skyscraper_solver_worker_") or f.startswith("benchmark_worker_"):
            try: os.remove(os.path.join(workspace, f))
            except: pass
            
    # Grid search parameters
    shallow_vals = [8, 12, 16, 20]
    deep_vals = [15, 20, 25, 30]
    reiterate_vals = [1, 2, 3]
    
    # Gather original C files once, explicitly excluding any worker/test C files
    base_c_files = [
        os.path.join(src_dir, f)
        for f in os.listdir(src_dir)
        if f.endswith(".c") and f != "node_pruning.c" and not f.startswith("node_pruning_worker_")
    ]
    
    # Create the subset of first 50 cases of size 7
    subset_50 = os.path.join(workspace, "benchmark_sets", "benchmarkSet7_subset50.txt")
    with open(os.path.join(workspace, "benchmark_sets", "benchmarkSet7.txt"), 'r') as f:
        lines = f.readlines()
    with open(subset_50, 'w') as f:
        f.writelines(lines[:50])
        
    print("=" * 80)
    print("CONCURRENT HYPERPARAMETER TUNER FOR SKYSCRAPER SOLVER")
    print("=" * 80)
    print(f"Created fast 50-case size 7 tuning subset.")
    print(f"Grid search space size: {len(shallow_vals) * len(deep_vals) * len(reiterate_vals)} combinations.")
    print("Starting concurrent execution...")
    print("-" * 80)
    
    results_grid = []
    
    # Compile a task list
    configs = []
    idx = 1
    for shallow in shallow_vals:
        for deep in deep_vals:
            for reiterate in reiterate_vals:
                configs.append((idx, shallow, deep, reiterate))
                idx += 1
                
    start_time = time.time()
    
    # Use ThreadPoolExecutor to run tasks concurrently
    max_workers = 8
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(evaluate_config, cfg[0], cfg[1], cfg[2], cfg[3], workspace, subset_50, base_c_files): cfg
            for cfg in configs
        }
        
        completed_count = 0
        for future in as_completed(futures):
            cfg = futures[future]
            res = future.result()
            completed_count += 1
            if res:
                results_grid.append(res)
                print(f"[{completed_count:2d}/{len(configs):2d}] Params: (shallow={res['shallow']:2d}, deep={res['deep']:2d}, reiterate={res['reiterate']}) -> Nodes: {res['nodes']:10,} | Time: {res['time']:5.2f}s")
            else:
                print(f"[{completed_count:2d}/{len(configs):2d}] Config {cfg[1:]} failed!")
                
    # Clean up the subset file
    if os.path.exists(subset_50):
        os.remove(subset_50)
        
    total_elapsed = time.time() - start_time
    print("-" * 80)
    print(f"Concurrent tuning completed in {total_elapsed:.2f} seconds.")
    print("=" * 80)
    
    if not results_grid:
        print("Error: No successful runs completed.")
        return
        
    # Find best parameter sets
    best_by_nodes = min(results_grid, key=lambda x: x["nodes"])
    best_by_time = min(results_grid, key=lambda x: x["time"])
    
    print(f"Absolute Mathematically Best Parameters by Node Count:")
    print(f" -> shallow={best_by_nodes['shallow']}, deep={best_by_nodes['deep']}, reiterate={best_by_nodes['reiterate']}")
    print(f" -> Total Nodes: {best_by_nodes['nodes']:,} | Total Time: {best_by_nodes['time']:.2f}s")
    print()
    print(f"Absolute Mathematically Best Parameters by Solver Execution Time:")
    print(f" -> shallow={best_by_time['shallow']}, deep={best_by_time['deep']}, reiterate={best_by_time['reiterate']}")
    print(f" -> Total Nodes: {best_by_time['nodes']:,} | Total Time: {best_by_time['time']:.2f}s")
    
    # Print sorted results (Top 10 by node count)
    print("\nTop 10 Parameter Settings (sorted by Search Node Count):")
    sorted_grid = sorted(results_grid, key=lambda x: x["nodes"])
    for idx, r in enumerate(sorted_grid[:10]):
        print(f"{idx+1:2d}. (shallow={r['shallow']:2d}, deep={r['deep']:2d}, reiterate={r['reiterate']}) -> Nodes: {r['nodes']:10,} | Time: {r['time']:5.2f}s")

if __name__ == "__main__":
    run_tuning()
