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
        line_lower = line.lower()
        if "solutions found" in line_lower or "unique solutions found" in line_lower:
            try:
                if ":" in line:
                    solutions_found = int(line.split(":")[1].strip())
                else:
                    solutions_found = int(line.split()[-1].strip())
            except ValueError:
                pass
        elif "unsatisfiable" in line_lower or "no solution found" in line_lower:
            solutions_found = 0
        elif line.startswith("Nodes visited:"):
            try:
                nodes_visited = int(line.split(":")[1].strip())
            except ValueError:
                pass
                
    if solutions_found is None:
        return {"error": f"Could not find solutions count in stdout. Output: {stdout}"}
        
    return {"solutions": solutions_found, "nodes": nodes_visited}

def verify_instance(idx, clues, binary_candidate, binary_reference, options, expected_solutions=None):
    res_candidate = run_solver(binary_candidate, options, clues)
    res_reference = run_solver(binary_reference, options, clues) if binary_reference else None
    return idx, clues, res_candidate, res_reference, expected_solutions

def verify_file(benchmark_file, expected_file, candidate, reference, options, jobs, num_instances=None):
    if not os.path.exists(benchmark_file):
        print(f"Error: Benchmark file {benchmark_file} not found.")
        return False
        
    expected_counts = None
    if expected_file:
        if not os.path.exists(expected_file):
            print(f"Error: Expected solutions file {expected_file} not found.")
            return False
        with open(expected_file, "r") as f:
            expected_counts = [int(line.strip()) for line in f if line.strip()]
            
    if not reference and not expected_file:
        print("Error: Must provide either a reference binary (-r) or expected solution counts file (-e).")
        return False

    with open(benchmark_file, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    if num_instances is not None:
        lines = lines[:num_instances]
        if expected_counts is not None:
            expected_counts = expected_counts[:num_instances]
        
    total = len(lines)
    print(f"Starting verification of {total} instances using {options}...")
    print(f"Benchmark file:   {benchmark_file}")
    print(f"Candidate binary: {candidate}")
    if reference:
        print(f"Reference binary: {reference}")
    if expected_file:
        print(f"Expected solutions file: {expected_file}")
    print("-" * 60)
    
    mismatches = 0
    errors = 0
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = [
            executor.submit(
                verify_instance, 
                idx, 
                line, 
                candidate, 
                reference, 
                options,
                expected_counts[idx - 1] if expected_counts is not None else None
            )
            for idx, line in enumerate(lines, 1)
        ]
        
        for fut in concurrent.futures.as_completed(futures):
            idx, clues, res_candidate, res_reference, expected_solutions = fut.result()
            
            if "error" in res_candidate or (res_reference and "error" in res_reference):
                errors += 1
                print(f"[ERROR] Instance {idx}:")
                if "error" in res_candidate:
                    print(f"  Candidate: {res_candidate['error']}")
                if res_reference and "error" in res_reference:
                    print(f"  Reference: {res_reference['error']}")
            else:
                s_candidate = res_candidate["solutions"]
                n_candidate = res_candidate["nodes"]
                
                # Check consistency against expected solutions if file was provided
                if expected_solutions is not None:
                    if s_candidate != expected_solutions:
                        mismatches += 1
                        print(f"[MISMATCH] Instance {idx} (Clues: {clues[:30]}...):")
                        print(f"  Candidate solutions: {s_candidate} (Nodes: {n_candidate})")
                        print(f"  Expected solutions:  {expected_solutions}")
                        continue
                
                # Check consistency between candidate and reference solvers if reference is provided
                if res_reference:
                    s_reference = res_reference["solutions"]
                    n_reference = res_reference["nodes"]
                    if s_candidate != s_reference:
                        mismatches += 1
                        print(f"[MISMATCH] Instance {idx} (Clues: {clues[:30]}...):")
                        print(f"  Candidate solutions: {s_candidate} (Nodes: {n_candidate})")
                        print(f"  Reference solutions: {s_reference} (Nodes: {n_reference})")
                        continue
                    results.append((idx, s_candidate, n_candidate, n_reference))
                else:
                    results.append((idx, s_candidate, n_candidate, 0))
                    
                # Print progress periodically
                if len(results) % max(1, total // 10) == 0 or len(results) == total:
                    print(f"Progress: {len(results)}/{total} verified successfully.")
                        
    print("-" * 60)
    print(f"Verification completed:")
    print(f"  Total instances checked: {total}")
    print(f"  Matches:                 {total - mismatches - errors}")
    print(f"  Mismatches:              {mismatches}")
    print(f"  Errors/Crashes:          {errors}")
    
    return mismatches == 0 and errors == 0

def main():
    parser = argparse.ArgumentParser(description="Verify solution count consistency between candidate and reference C solvers.")
    parser.add_argument("benchmark_file", nargs="?", default=None, help="Path to the benchmark set file. If omitted, runs default Size 7 and Size 8 tests.")
    parser.add_argument("-c", "--candidate", default="./skyscraper_solver", help="Path to the candidate solver binary.")
    parser.add_argument("-r", "--reference", default=None, help="Path to the reference solver binary (optional).")
    parser.add_argument("-e", "--expected", default=None, help="Path to the expected solution counts file.")
    parser.add_argument("-o", "--options", default="-s 0", help="Options for both solvers.")
    parser.add_argument("-j", "--jobs", type=int, default=8, help="Number of concurrent verification jobs.")
    parser.add_argument("-n", "--num_instances", type=int, default=None, help="Limit to first N instances.")
    
    args = parser.parse_args()
    
    candidate_path = os.path.abspath(args.candidate)
    reference_path = os.path.abspath(args.reference) if args.reference else None
    
    try:
        subprocess.run([candidate_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print(f"Error: Candidate binary {candidate_path} not found. Please compile it first.")
        sys.exit(1)
        
    if reference_path:
        try:
            subprocess.run([reference_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print(f"Error: Reference binary {reference_path} not found. Please compile it first.")
            sys.exit(1)
        
    if args.benchmark_file is not None:
        success = verify_file(args.benchmark_file, args.expected, candidate_path, reference_path, args.options, args.jobs, args.num_instances)
        if not success:
            print("[FAIL] Mismatches or errors were found!")
            sys.exit(1)
        else:
            print("[SUCCESS] All checked solution counts are 100% consistent!")
            sys.exit(0)
    else:
        # Run default sets
        print("No benchmark file provided. Running default verification on Size 7 and Size 8 sets...")
        default_sets = [
            ("benchmark_sets/benchmarkSet7_easy500.txt", "benchmark_sets/_num_solutions_benchmarkSet7_easy500.txt"),
            ("benchmark_sets/benchmarkSet8_easy50.txt", "benchmark_sets/_num_solutions_benchmarkSet8_easy50.txt")
        ]
        all_success = True
        for b_file, e_file in default_sets:
            print(f"\n============================================================")
            print(f"Running Default Set: {b_file}")
            print(f"============================================================")
            success = verify_file(b_file, e_file, candidate_path, reference_path, args.options, args.jobs, args.num_instances)
            if not success:
                all_success = False
        
        if not all_success:
            print("\n[FAIL] Mismatches or errors were found in one or more default sets!")
            sys.exit(1)
        else:
            print("\n[SUCCESS] All default sets checked solution counts are 100% consistent!")
            sys.exit(0)

if __name__ == "__main__":
    main()
