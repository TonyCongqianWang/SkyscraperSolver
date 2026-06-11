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

def evaluate(benchmark_file, options):
    with open(benchmark_file, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    ref_total_nodes = 0
    ref_total_time = 0.0
    base_total_nodes = 0
    base_total_time = 0.0
    
    for clues in lines:
        res_ref = run_solver("./skyscraper_solver", options, clues)
        res_base = run_solver("./skyscraper_solver_main", options, clues)
        
        if "error" in res_ref or "error" in res_base:
            continue
            
        ref_total_nodes += res_ref["nodes"]
        ref_total_time += res_ref["time"]
        base_total_nodes += res_base["nodes"]
        base_total_time += res_base["time"]
        
    node_red = (base_total_nodes - ref_total_nodes) / base_total_nodes * 100 if base_total_nodes else 0
    speedup = (base_total_time - ref_total_time) / base_total_time * 100 if base_total_time else 0
    
    return ref_total_nodes, base_total_nodes, node_red, ref_total_time, base_total_time, speedup

def main():
    benchmark_file = "benchmark_sets/benchmarkSet7_rand100.txt"
    options = "-s 0"
    
    prune_periods = [8, 16, 24, 32, 48, 64]
    prune_deeps = [15, 30, 45, 60, 90, 120]
    
    print(f"| G_PRUNE_PERIOD_SHALLOW | G_PRUNE_EXTRA_PERIOD_DEEP | Ref Nodes | Base Nodes | Node Red % | Ref Time | Base Time | Speedup % |")
    print(f"|---|---|---|---|---|---|---|---|")
    
    for pd in prune_deeps:
        for pp in prune_periods:
            # Recompile
            cflags = f"-Wall -Wextra -Werror -O2 -DG_PRUNE_PERIOD_SHALLOW={pp} -DG_PRUNE_EXTRA_PERIOD_DEEP={pd} -DREBUILD_PERIOD=4 -DREBUILD_IN_LOOKAHEAD=0"
            run_cmd("make clean")
            code, out, err = run_cmd(f"make CFLAGS='{cflags}'")
            if code != 0:
                print(f"Compile failed for pp={pp}, pd={pd}: {err}")
                continue
                
            ref_nodes, base_nodes, node_red, ref_time, base_time, speedup = evaluate(benchmark_file, options)
            print(f"| {pp} | {pd} | {ref_nodes} | {base_nodes} | {node_red:.2f}% | {ref_time:.3f}s | {base_time:.3f}s | {speedup:.2f}% |")

if __name__ == "__main__":
    main()
