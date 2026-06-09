#!/usr/bin/env python3
import subprocess
import time
import sys
import os

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

def evaluate_solvers(benchmark_file, options, step2_binary):
    with open(benchmark_file, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    results = {
        "base": {"nodes": 0, "time": 0.0},
        "step1": {"nodes": 0, "time": 0.0},
        "step2": {"nodes": 0, "time": 0.0}
    }
    
    for clues in lines:
        res_base = run_solver("./skyscraper_solver_main", options, clues)
        res_step1 = run_solver("./skyscraper_solver_step1", options, clues)
        res_step2 = run_solver(step2_binary, options, clues)
        
        if "error" in res_base or "error" in res_step1 or "error" in res_step2:
            continue
            
        results["base"]["nodes"] += res_base["nodes"]
        results["base"]["time"] += res_base["time"]
        
        results["step1"]["nodes"] += res_step1["nodes"]
        results["step1"]["time"] += res_step1["time"]
        
        results["step2"]["nodes"] += res_step2["nodes"]
        results["step2"]["time"] += res_step2["time"]
        
    return results

def main():
    benchmark_file = "benchmark_sets/benchmarkSet8_subset300.txt"
    options = "-s 1"
    
    # We keep shallow/deep pruning periods at 16/15, but vary REBUILD_PERIOD (rp) to high values
    sweeps = [
        {"rp": 16, "ps": 16, "pd": 15, "ur": 0.40},
        {"rp": 32, "ps": 16, "pd": 15, "ur": 0.40},
        {"rp": 64, "ps": 16, "pd": 15, "ur": 0.40},
        {"rp": 128, "ps": 16, "pd": 15, "ur": 0.40},
        {"rp": 256, "ps": 16, "pd": 15, "ur": 0.40},
        {"rp": 512, "ps": 16, "pd": 15, "ur": 0.40},
        {"rp": 99999, "ps": 16, "pd": 15, "ur": 0.40}, # basically never rebuild in tree search (rebuild only once at root)
    ]
    
    print(f"| REBUILD_PERIOD | SHALLOW | DEEP | UNSET_RATIO | Base Nodes | Step1 Nodes | Step2 Nodes | Base Time | Step1 Time | Step2 Time | Step2 NodeRed % | Step2 Speedup % |")
    print(f"|---|---|---|---|---|---|---|---|---|---|---|---|")
    
    for cfg in sweeps:
        rp, ps, pd, ur = cfg["rp"], cfg["ps"], cfg["pd"], cfg["ur"]
        cflags = f"-Wall -Wextra -Werror -O2 -DREBUILD_PERIOD={rp} -DG_PRUNE_PERIOD_SHALLOW={ps} -DG_PRUNE_EXTRA_PERIOD_DEEP={pd} -DG_MIN_UNSET_R_PRUNE={ur} -DREBUILD_IN_LOOKAHEAD=0"
        
        run_cmd("make clean")
        code, out, err = run_cmd(f"make CFLAGS='{cflags}'")
        if code != 0:
            print(f"Compile failed: {err}")
            continue
            
        res = evaluate_solvers(benchmark_file, options, "./skyscraper_solver")
        
        base_nodes = res["base"]["nodes"]
        base_time = res["base"]["time"]
        step1_nodes = res["step1"]["nodes"]
        step1_time = res["step1"]["time"]
        step2_nodes = res["step2"]["nodes"]
        step2_time = res["step2"]["time"]
        
        node_red = (base_nodes - step2_nodes) / base_nodes * 100 if base_nodes else 0
        speedup = (base_time - step2_time) / base_time * 100 if base_time else 0
        
        print(f"| {rp} | {ps} | {pd} | {ur:.2f} | {base_nodes} | {step1_nodes} | {step2_nodes} | {base_time:.3f}s | {step1_time:.3f}s | {step2_time:.3f}s | {node_red:.2f}% | {speedup:.2f}% |")

if __name__ == "__main__":
    main()
