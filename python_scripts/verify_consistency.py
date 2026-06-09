#!/usr/bin/env python3
import subprocess
import sys
import shlex
import concurrent.futures
import argparse
import os

def run_solver(binary, options, clues):
    cmd = [binary] + shlex.split(options) + [clues]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate()
    except Exception as e:
        return {"error": f"Failed to execute: {e}"}
    
    if proc.returncode != 0:
        return {"error": f"Exit code {proc.returncode}. Stderr: {stderr.strip()}"}
    
    solutions_found = None
    nodes_visited = None
    for line in stdout.splitlines():
        if line.startswith("Solutions found:"):
            try:
                solutions_found = int(line.split(":")[1].strip())
            except ValueError:
                pass
        elif line.startswith("Nodes visited:"):
            try:
                nodes_visited = int(line.split(":")[1].strip())
            except ValueError:
                pass
                
    if solutions_found is None:
        return {"error": f"Could not find solutions count in stdout. Output: {stdout}"}
        
    return {"solutions": solutions_found, "nodes": nodes_visited}

def verify_instance(idx, clues, binary_refactored, binary_baseline, options, expected_solutions=None):
    res_ref = run_solver(binary_refactored, options, clues)
    if expected_solutions is not None:
        res_base = {"solutions": expected_solutions}
    else:
        res_base = run_solver(binary_baseline, options, clues)
    
    return idx, clues, res_ref, res_base

def main():
    parser = argparse.ArgumentParser(description="Verify solution count consistency between refactored and baseline C solvers.")
    parser.add_argument("benchmark_file", help="Path to the benchmark set file.")
    parser.add_argument("-r", "--refactored", default="./skyscraper_solver", help="Path to the refactored binary.")
    parser.add_argument("-b", "--baseline", default="./skyscraper_solver_main", help="Path to the baseline binary.")
    parser.add_argument("-e", "--expected", default=None, help="Path to the expected solution counts file.")
    parser.add_argument("-o", "--options", default="-s 0", help="Options for both solvers.")
    parser.add_argument("-j", "--jobs", type=int, default=8, help="Number of concurrent verification jobs.")
    parser.add_argument("-n", "--num_instances", type=int, default=None, help="Limit to first N instances.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.benchmark_file):
        print(f"Error: Benchmark file {args.benchmark_file} not found.")
        sys.exit(1)
        
    if not os.path.exists(args.refactored):
        print(f"Error: Binary {args.refactored} not found. Please compile it first.")
        sys.exit(1)
        
    if args.expected:
        if not os.path.exists(args.expected):
            print(f"Error: Expected solutions file {args.expected} not found.")
            sys.exit(1)
    else:
        if not os.path.exists(args.baseline):
            print(f"Error: Baseline binary {args.baseline} not found. Please compile it first or provide --expected.")
            sys.exit(1)
            
    with open(args.benchmark_file, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    expected_counts = None
    if args.expected:
        with open(args.expected, "r") as f:
            expected_counts = [int(line.strip()) for line in f if line.strip()]
        if len(expected_counts) < len(lines):
            print(f"Warning: Expected solutions file has fewer lines ({len(expected_counts)}) than benchmark file ({len(lines)}).")
            
    if args.num_instances is not None:
        lines = lines[:args.num_instances]
        if expected_counts is not None:
            expected_counts = expected_counts[:args.num_instances]
        
    total = len(lines)
    print(f"Starting verification of {total} instances using {args.options}...")
    print(f"Refactored binary: {args.refactored}")
    if args.expected:
        print(f"Expected solutions file: {args.expected}")
    else:
        print(f"Baseline binary:   {args.baseline}")
    print("-" * 60)
    
    mismatches = 0
    errors = 0
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [
            executor.submit(
                verify_instance, 
                idx, 
                line, 
                args.refactored, 
                args.baseline, 
                args.options,
                expected_counts[idx - 1] if expected_counts is not None else None
            )
            for idx, line in enumerate(lines, 1)
        ]
        
        for fut in concurrent.futures.as_completed(futures):
            idx, clues, res_ref, res_base = fut.result()
            
            if "error" in res_ref or "error" in res_base:
                errors += 1
                print(f"[ERROR] Instance {idx}:")
                if "error" in res_ref:
                    print(f"  Refactored: {res_ref['error']}")
                if "error" in res_base:
                    print(f"  Expected/Baseline:   {res_base['error']}")
            else:
                s_ref = res_ref["solutions"]
                s_base = res_base["solutions"]
                n_ref = res_ref["nodes"]
                n_base = res_base.get("nodes", 0)
                
                if s_ref != s_base:
                    mismatches += 1
                    print(f"[MISMATCH] Instance {idx} (Clues: {clues[:30]}...):")
                    print(f"  Refactored solutions: {s_ref} (Nodes: {n_ref})")
                    print(f"  Expected solutions:   {s_base}")
                else:
                    results.append((idx, s_ref, n_ref, n_base))
                    # Print progress periodically
                    if len(results) % max(1, total // 10) == 0 or len(results) == total:
                        print(f"Progress: {len(results)}/{total} verified successfully.")
                        
    print("-" * 60)
    print(f"Verification completed:")
    print(f"  Total instances checked: {total}")
    print(f"  Matches:                 {total - mismatches - errors}")
    print(f"  Mismatches:              {mismatches}")
    print(f"  Errors/Crashes:          {errors}")
    
    if mismatches > 0 or errors > 0:
        print("[FAIL] Mismatches or errors were found!")
        sys.exit(1)
    else:
        print("[SUCCESS] All checked solution counts are 100% consistent!")
        sys.exit(0)

if __name__ == "__main__":
    main()
