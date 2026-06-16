import os
import sys
import subprocess
import time
import argparse
from multiprocessing import Pool

def get_symmetries(T, B, L, R):
    s1 = (T, B, L, R)
    s2 = (L[::-1], R[::-1], B, T)
    s3 = (B[::-1], T[::-1], R[::-1], L[::-1])
    s4 = (R, L, T[::-1], B[::-1])
    s5 = (T[::-1], B[::-1], R, L)
    s6 = (R[::-1], L[::-1], B[::-1], T[::-1])
    s7 = (B, T, L[::-1], R[::-1])
    s8 = (L, R, T, B)
    return [s1, s2, s3, s4, s5, s6, s7, s8]

def canonize(nums):
    """
    Dynamically determines board size based on clue count.
    Standard skyscraper clues have 4 sides, so grid size N = len(nums) // 4.
    """
    n = len(nums) // 4
    T = nums[0:n]
    B = nums[n:2*n]
    L = nums[2*n:3*n]
    R = nums[3*n:4*n]
    symmetries = get_symmetries(T, B, L, R)
    sym_lists = [s[0] + s[1] + s[2] + s[3] for s in symmetries]
    return tuple(min(sym_lists))

def load_and_canonize_files(filepaths, is_exclude_set=False):
    """Parses files and yields (cmd_str, canonical_key) tuples."""
    instances = []
    set_type = "Negative" if is_exclude_set else "Positive"
    
    for path in filepaths:
        if not os.path.exists(path):
            print(f"Error: {set_type} benchmark file not found at {path}")
            sys.exit(1)
            
        with open(path, 'r') as f:
            lines = [l.strip().strip('"') for l in f if l.strip()]
            
        for idx, line in enumerate(lines):
            try:
                nums = list(map(int, line.split()))
                if len(nums) == 0 or len(nums) % 4 != 0:
                    print(f"Warning: {path} Line {idx+1} has invalid clue count. Skipping.")
                    continue
                key = canonize(nums)
                instances.append((line, key))
            except ValueError:
                print(f"Warning: {path} Line {idx+1} contains invalid numeric data. Skipping.")
                
    return instances

def run_pre_screen(args):
    """Run solver with a specific solution limit and timeout to estimate density."""
    idx, cmd_str, solver_path, prescreen_sols, timeout = args
    try:
        t0 = time.time()
        res = subprocess.run(
            [solver_path, "-s", str(prescreen_sols), cmd_str], 
            capture_output=True, text=True, timeout=timeout
        )
        t1 = time.time()

        if res.returncode != 0:
            return idx, cmd_str, "error", 0, 999999999, timeout

        sols = 0
        nodes = 0
        for line in res.stdout.splitlines():
            if line.startswith("Solutions found:"):
                sols = int(line.split(":")[1].strip())
            elif line.startswith("Nodes visited:"):
                nodes = int(line.split(":")[1].strip())

        return idx, cmd_str, "success", sols, nodes, t1 - t0
    except subprocess.TimeoutExpired:
        return idx, cmd_str, "timeout", 0, 999999999, timeout
    except Exception as e:
        return idx, cmd_str, "error", 0, 999999999, timeout

def run_full_enum(args):
    """Run solver with -s 0 (full enumeration) and a specific timeout."""
    idx, cmd_str, solver_path, timeout = args
    try:
        t0 = time.time()
        res = subprocess.run(
            [solver_path, "-s", "0", cmd_str], 
            capture_output=True, text=True, timeout=timeout
        )
        t1 = time.time()

        if res.returncode == 0:
            nodes = 0
            sols_found = 0
            for line in res.stdout.splitlines():
                if line.startswith("Nodes visited:"):
                    nodes = int(line.split(":")[1].strip())
                elif line.startswith("Solutions found:"):
                    sols_found = int(line.split(":")[1].strip())
            return {
                "idx": idx,
                "cmd_str": cmd_str,
                "status": "success",
                "nodes": nodes,
                "sols_found": sols_found,
                "time": t1 - t0
            }
        else:
            return {
                "idx": idx,
                "cmd_str": cmd_str,
                "status": f"failed_code_{res.returncode}"
            }
    except subprocess.TimeoutExpired:
        return {"idx": idx, "cmd_str": cmd_str, "status": "timeout"}
    except Exception as e:
        return {"idx": idx, "cmd_str": cmd_str, "status": f"error_{str(e)}"}

def parse_args():
    parser = argparse.ArgumentParser(description="Skyscraper puzzle enumeration and filtering tool.")
    parser.add_argument("--binary", type=str, 
                        default="./skyscraper_solver_main", 
                        help="Path to the solver executable (defaults to ./skyscraper_solver_main).")
    parser.add_argument("--benchmarks", type=str, nargs='+', required=True,
                        help="One or more paths to positive benchmark input files (union).")
    parser.add_argument("--exclude", type=str, nargs='+', default=[],
                        help="One or more paths to negative benchmark files to filter out.")
    parser.add_argument("--timeout", type=float, default=60.0, 
                        help="Timeout for the full enumeration runs (seconds).")
    parser.add_argument("--prescreen-timeout", type=float, default=None, 
                        help="Timeout for pre-screening. Defaults to (max(0, timeout-0.05)/100) + 0.05.")
    parser.add_argument("--prescreen-sols", type=int, default=10, 
                        help="Maximum solutions to search for during pre-screening (-s argument).")
    parser.add_argument("--output", type=str, default=None, 
                        help="Optional filepath to save discovered solvable instances.")
    parser.add_argument("--max-solved", type=int, default=50, 
                        help="Limit the number of fully solved instances to find before halting.")
    parser.add_argument("--workers", type=int, default=None, 
                        help="Number of CPU workers to use. Defaults to system core count.")
    return parser.parse_args()

def main():
    args = parse_args()

    if args.prescreen_timeout is None:
        args.prescreen_timeout = (max(0.0, args.timeout - 0.05) / 100.0) + 0.05

    num_cpus = args.workers if args.workers is not None else (os.cpu_count() or 4)
    
    if not os.path.exists(args.binary):
        print(f"Error: Solver binary not found at '{args.binary}'")
        sys.exit(1)

    # 1. Process exclusions to prepopulate the seen set
    seen = set()
    if args.exclude:
        print(f"Loading exclusions from {len(args.exclude)} file(s)...", flush=True)
        neg_instances = load_and_canonize_files(args.exclude, is_exclude_set=True)
        for _, key in neg_instances:
            seen.add(key)
        print(f"Loaded {len(seen)} unique exclusions.", flush=True)

    # 2. Process positive inclusions and filter
    print(f"Loading positive benchmarks from {len(args.benchmarks)} file(s)...", flush=True)
    pos_instances = load_and_canonize_files(args.benchmarks, is_exclude_set=False)
    
    unique_instances = []
    current_idx = 1
    for cmd_str, key in pos_instances:
        if key not in seen:
            seen.add(key)
            unique_instances.append((current_idx, cmd_str))
            current_idx += 1

    if not unique_instances:
        print("No unique instances left to process after deduplication and exclusions. Exiting.")
        sys.exit(0)

    print(f"Found {len(unique_instances)} unique instances to process. Running with {num_cpus} workers.", flush=True)

    # Step 1: Pre-screen
    print(f"\nPre-screening instances (-s {args.prescreen_sols}, {args.prescreen_timeout:.3f}s timeout)...", flush=True)
    prescreen_args = [(idx, line, args.binary, args.prescreen_sols, args.prescreen_timeout) for idx, cmd_str in unique_instances for line in [cmd_str]]
    
    t0 = time.time()
    with Pool(processes=num_cpus) as pool:
        prescreen_results = pool.map(run_pre_screen, prescreen_args)
    t1 = time.time()
    print(f"Pre-screening completed in {t1 - t0:.2f} seconds.", flush=True)

    group1 = []
    group2 = []
    for idx, cmd_str, status, sols, nodes, duration in prescreen_results:
        if status == "success":
            if sols < args.prescreen_sols:
                group1.append((idx, cmd_str, sols, nodes, duration))
            else:
                group2.append((idx, cmd_str, sols, nodes, duration))

    # Sort Group 2 by time ascending
    group2.sort(key=lambda x: x[4])
    candidates = group1 + group2
    
    print(f"Pre-screened candidates: {len(group1)} finished completely, {len(group2)} hit the {args.prescreen_sols} solution limit.", flush=True)
    
    if not candidates:
        print("No valid candidates passed the pre-screening. Exiting.")
        sys.exit(0)
        
    print(f"Total candidates queued for full enumeration: {len(candidates)}", flush=True)

    solved_instances = {}

    # Step 2: Full Enumeration Run
    print(f"\nRunning full enumeration ({args.timeout}s timeout) on candidates...", flush=True)
    run_args = [(idx, cmd_str, args.binary, args.timeout) for idx, cmd_str, _, _, _ in candidates]

    with Pool(processes=num_cpus) as pool:
        try:
            for r in pool.imap_unordered(run_full_enum, run_args):
                if len(solved_instances) >= args.max_solved:
                    print(f"Reached maximum solved instances limit ({args.max_solved}). Stopping search.", flush=True)
                    pool.terminate()
                    break

                if r["status"] == "success":
                    solved_instances[r["idx"]] = r
                    print(f"  -> Solved: Process ID {r['idx']} in {r['time']:.2f}s (Sols: {r['sols_found']}, Nodes: {r['nodes']})", flush=True)
        except KeyboardInterrupt:
            print("\nExecution interrupted by user. Terminating pool...")
            pool.terminate()
            pool.join()
            sys.exit(1)

    solved_keys = sorted(solved_instances.keys())
    print(f"\nFound {len(solved_keys)} solvable instances in total.", flush=True)

    if args.output:
        print(f"Writing solvable instances to {args.output}...", flush=True)
        try:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "w") as out_f:
                for idx in solved_keys:
                    out_f.write(f'"{solved_instances[idx]["cmd_str"]}"\n')
            print("Write successful.")
        except Exception as e:
            print(f"Failed to write to {args.output}: {e}")
    else:
        print("No output file specified. Skipping file write.")

if __name__ == "__main__":
    main()
