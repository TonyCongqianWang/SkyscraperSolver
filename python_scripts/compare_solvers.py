#!/usr/bin/env python3
import subprocess
import sys
import time
import argparse
import os

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark_file")
    parser.add_argument("-r", "--refactored", default="./skyscraper_solver")
    parser.add_argument("-b", "--baseline", default="./skyscraper_solver_main")
    parser.add_argument("-o", "--options", default="-s 1")
    parser.add_argument("-n", "--num_instances", type=int, default=None)
    args = parser.parse_args()
    
    with open(args.benchmark_file, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    if args.num_instances is not None:
        lines = lines[:args.num_instances]
        
    print(f"Comparing solvers on {len(lines)} instances...")
    print(f"Refactored: {args.refactored}")
    print(f"Baseline:   {args.baseline}")
    print(f"Options:    {args.options}")
    print("-" * 50)
    
    ref_total_nodes = 0
    ref_total_time = 0.0
    base_total_nodes = 0
    base_total_time = 0.0
    
    for idx, clues in enumerate(lines, start=1):
        res_ref = run_solver(args.refactored, args.options, clues)
        res_base = run_solver(args.baseline, args.options, clues)
        
        if "error" in res_ref or "error" in res_base:
            print(f"Instance {idx} error: ref={res_ref.get('error')}, base={res_base.get('error')}")
            continue
            
        ref_total_nodes += res_ref["nodes"]
        ref_total_time += res_ref["time"]
        base_total_nodes += res_base["nodes"]
        base_total_time += res_base["time"]
        
    print("-" * 50)
    print(f"Refactored total nodes: {ref_total_nodes}")
    print(f"Baseline total nodes:   {base_total_nodes}")
    node_red = (base_total_nodes - ref_total_nodes) / base_total_nodes * 100 if base_total_nodes else 0
    print(f"Node Reduction:         {node_red:.2f}%")
    print("-" * 50)
    print(f"Refactored total time:  {ref_total_time:.3f}s")
    print(f"Baseline total time:    {base_total_time:.3f}s")
    time_red = (base_total_time - ref_total_time) / base_total_time * 100 if base_total_time else 0
    print(f"Speedup:                {time_red:.2f}%")

if __name__ == "__main__":
    main()
