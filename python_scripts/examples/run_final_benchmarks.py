#!/usr/bin/env python3
import subprocess
import sys
import time

def run_cmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr

def run_solver(binary, options, clues):
    cmd = [binary] + options.split() + [clues]
    start = time.time()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate()
    except Exception as e:
        return {"error": f"Failed: {e}"}
    elapsed = time.time() - start
    
    if proc.returncode != 0:
        return {"error": f"Exit {proc.returncode}"}
        
    solutions_found = 0
    nodes_visited = 0
    for line in stdout.splitlines():
        if line.startswith("Solutions found:"):
            solutions_found = int(line.split(":")[1].strip())
        elif line.startswith("Nodes visited:"):
            nodes_visited = int(line.split(":")[1].strip())
            
    return {"solutions": solutions_found, "nodes": nodes_visited, "time": elapsed}

def run_set(benchmark_file, options):
    with open(benchmark_file, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    ref_nodes, ref_time = 0, 0.0
    base_nodes, base_time = 0, 0.0
    
    for clues in lines:
        res_ref = run_solver("./skyscraper_solver", options, clues)
        res_base = run_solver("./skyscraper_solver_main", options, clues)
        
        if "error" in res_ref or "error" in res_base:
            continue
            
        ref_nodes += res_ref["nodes"]
        ref_time += res_ref["time"]
        base_nodes += res_base["nodes"]
        base_time += res_base["time"]
        
    return ref_nodes, base_nodes, ref_time, base_time

def main():
    print("Recompiling solver with optimized parameters...")
    cflags = "-Wall -Wextra -Werror -O2 -DREBUILD_PERIOD=4 -DG_PRUNE_PERIOD_SHALLOW=16 -DG_PRUNE_EXTRA_PERIOD_DEEP=15 -DREBUILD_IN_LOOKAHEAD=0"
    run_cmd("make clean")
    code, out, err = run_cmd(f"make CFLAGS='{cflags}'")
    if code != 0:
        print(f"Compilation failed: {err}")
        sys.exit(1)
    print("Compilation successful.")
    print("-" * 60)
    
    print("Running complete Size 7 Benchmark (6,000 instances, -s 0)...")
    r_n7, b_n7, r_t7, b_t7 = run_set("benchmark_sets/benchmarkSet7.txt", "-s 0")
    print(f"Size 7 Nodes: Ref={r_n7}, Base={b_n7} (Red={(b_n7-r_n7)/b_n7*100:.2f}%)")
    print(f"Size 7 Time:  Ref={r_t7:.3f}s, Base={b_t7:.3f}s (Speedup={(b_t7-r_t7)/b_t7*100:.2f}%)")
    print("-" * 60)
    
    print("Running complete Size 8 Benchmark (6,000 instances, -s 1)...")
    r_n8, b_n8, r_t8, b_t8 = run_set("benchmark_sets/benchmarkSet8.txt", "-s 1")
    print(f"Size 8 Nodes: Ref={r_n8}, Base={b_n8} (Red={(b_n8-r_n8)/b_n8*100:.2f}%)")
    print(f"Size 8 Time:  Ref={r_t8:.3f}s, Base={b_t8:.3f}s (Speedup={(b_t8-r_t8)/b_t8*100:.2f}%)")
    print("-" * 60)

if __name__ == "__main__":
    main()
