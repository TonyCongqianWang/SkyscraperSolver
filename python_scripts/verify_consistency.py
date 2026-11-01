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

def run_pass(name, instances, candidate, reference, options, jobs):
    """Execute one verification mode across its entire selected dataset."""
    print(f"  Pass: {name} ({len(instances)} instances, {options})", flush=True)

    def check(item):
        idx, clues, expected = item
        result = run_solver(candidate, options, clues)
        if "error" in result:
            return idx, f"candidate error: {result['error']}"
        wanted = min(int(shlex.split(options)[1]), expected) if options != "-s 0" else expected
        if result["solutions"] != wanted:
            return idx, f"got {result['solutions']}, expected {wanted} (nodes: {result['nodes']})"
        if reference:
            ref_result = run_solver(reference, options, clues)
            if "error" in ref_result:
                return idx, f"reference error: {ref_result['error']}"
            if result["solutions"] != ref_result["solutions"]:
                return idx, f"candidate {result['solutions']} vs reference {ref_result['solutions']}"
        return idx, None

    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = [executor.submit(check, item) for item in instances]
        for future in concurrent.futures.as_completed(futures):
            idx, error = future.result()
            if error:
                failures += 1
                print(f"[FAIL] {name}, instance {idx}: {error}")
    print(f"  {name}: {len(instances) - failures}/{len(instances)} passed", flush=True)
    return failures == 0


def verify_file(benchmark_file, expected_file, candidate, reference, options, jobs,
                num_instances=None, limit_instances=None):
    if not os.path.exists(benchmark_file):
        print(f"Error: Benchmark file {benchmark_file} not found.")
        return False

    if not expected_file:
        print("Error: An expected-count file is required for ordered multi-pass checks.")
        return False
    if not os.path.exists(expected_file):
        print(f"Error: Expected solutions file {expected_file} not found.")
        return False

    with open(benchmark_file, "r") as stream:
        clues = [line.strip().strip('"') for line in stream if line.strip()]
    with open(expected_file, "r") as stream:
        expected = [int(line.strip()) for line in stream if line.strip()]

    if len(expected) != len(clues):
        print(f"Error: {benchmark_file} has {len(clues)} puzzles, but {expected_file} "
              f"has {len(expected)} expected counts.")
        return False

    total = min(len(clues), num_instances) if num_instances is not None else len(clues)
    items = [(i + 1, clues[i], expected[i]) for i in range(total)]
    limit_count = min(total, limit_instances) if limit_instances is not None else total
    limited_items = items[:limit_count]

    print(f"Dataset: {benchmark_file}")
    print(f"  Enumeration: {total} instances")
    print(f"  Finite limits: first {limit_count} instances")

    # Finish all exhaustive checks before starting any limited-search pass.
    success = run_pass("enumeration", items, candidate, reference, options, jobs)
    success = run_pass("-s 10", limited_items, candidate, None, "-s 10", jobs) and success

    # Each instance has its own exact count; execute these in a separate pass.
    exact_items = [item for item in limited_items if item[2] > 0]
    print(f"  Pass: exact count ({len(exact_items)} instances)", flush=True)
    failures = 0

    def exact_check(item):
        idx, clue, count = item
        result = run_solver(candidate, f"-s {count}", clue)
        if "error" in result:
            return idx, result["error"]
        if result["solutions"] != count:
            return idx, f"got {result['solutions']}, expected {count}"
        return idx, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = [executor.submit(exact_check, item) for item in exact_items]
        for future in concurrent.futures.as_completed(futures):
            idx, error = future.result()
            if error:
                failures += 1
                print(f"[FAIL] exact-count instance {idx}: {error}")
    print(f"  Exact count: {len(exact_items) - failures}/{len(exact_items)} passed")
    return success and failures == 0


def main():
    parser = argparse.ArgumentParser(description="Verify solution count consistency between candidate and reference C solvers.")
    parser.add_argument("benchmark_file", nargs="?", default=None, help="Path to the benchmark set file. If omitted, runs default Size 7 and Size 8 tests.")
    parser.add_argument("-c", "--candidate", default="./skyscraper_solver", help="Path to the candidate solver binary.")
    parser.add_argument("-r", "--reference", default=None, help="Path to the reference solver binary (optional).")
    parser.add_argument("-e", "--expected", default=None, help="Path to the expected solution counts file.")
    parser.add_argument("-o", "--options", default="-s 0", help="Options for both solvers.")
    parser.add_argument("-j", "--jobs", type=int, default=8, help="Number of concurrent verification jobs.")
    parser.add_argument("-n", "--num_instances", type=int, default=None, help="Limit enumeration and finite checks to first N instances.")
    parser.add_argument("--limit-instances", type=int, default=None, help="Check finite limits only on the first N instances (enumerate all).")
    
    args = parser.parse_args()
    if args.jobs < 1 or (args.num_instances is not None and args.num_instances < 1) or (args.limit_instances is not None and args.limit_instances < 0):
        parser.error("jobs and num_instances must be positive; limit-instances must be nonnegative")
    
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
        success = verify_file(args.benchmark_file, args.expected, candidate_path, reference_path, args.options, args.jobs, args.num_instances, args.limit_instances)
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
        # Regression: the old finite-limit accounting returned only 1 for -s 2,
        # although exhaustive enumeration correctly found 2 solutions.
        regression_clues = "1 3 3 0 0 0 0 2 0 0 0 0 0 0 0 0"
        print("\\nRunning finite-limit 4x4 regression...")
        for limit, expected in ((0, 2), (1, 1), (2, 2), (10, 2)):
            result = run_solver(candidate_path, f"-s {limit}", regression_clues)
            if "error" in result or result["solutions"] != expected:
                print(f"[FAIL] Regression -s {limit}: {result}, expected {expected}")
                all_success = False
            else:
                print(f"[PASS] Regression -s {limit}: {expected} solutions")
        for b_file, e_file in default_sets:
            print(f"\n============================================================")
            print(f"Running Default Set: {b_file}")
            print(f"============================================================")
            success = verify_file(b_file, e_file, candidate_path, reference_path, args.options, args.jobs, args.num_instances, 10 if "benchmarkSet8_" in b_file else args.limit_instances)
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
