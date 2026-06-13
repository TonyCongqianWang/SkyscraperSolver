import os
import subprocess
import time
import sys
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
    T = nums[0:9]
    B = nums[9:18]
    L = nums[18:27]
    R = nums[27:36]
    symmetries = get_symmetries(T, B, L, R)
    sym_lists = [s[0] + s[1] + s[2] + s[3] for s in symmetries]
    return tuple(min(sym_lists))

def run_single_sol(args):
    """Run solver with -s 1 (find first solution) to estimate difficulty."""
    idx, cmd_str, solver_path = args
    try:
        t0 = time.time()
        res = subprocess.run([solver_path, cmd_str], capture_output=True, text=True, timeout=1.0)
        t1 = time.time()
        nodes = 999999999
        for line in res.stdout.splitlines():
            if line.startswith("Nodes visited:"):
                nodes = int(line.split(":")[1].strip())
                break
        return idx, cmd_str, nodes, t1 - t0
    except subprocess.TimeoutExpired:
        return idx, cmd_str, 999999999, 1.0
    except Exception as e:
        return idx, cmd_str, 999999999, 1.0

def run_full_enum(args):
    """Run solver with -s 0 (full enumeration) and a specific timeout."""
    idx, cmd_str, solver_path, timeout = args
    try:
        t0 = time.time()
        res = subprocess.run([solver_path, "-s", "0", cmd_str], capture_output=True, text=True, timeout=timeout)
        t1 = time.time()
        
        # Check if it completed successfully
        if res.returncode == 0:
            stdout = res.stdout
            # Extract nodes and solutions count
            nodes = 0
            sols_found = 0
            lines = stdout.splitlines()
            for line in lines:
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
                "time": t1 - t0,
                "stdout": stdout
            }
        else:
            return {
                "idx": idx,
                "cmd_str": cmd_str,
                "status": f"failed_code_{res.returncode}",
                "stdout": res.stdout,
                "stderr": res.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "idx": idx,
            "cmd_str": cmd_str,
            "status": "timeout"
        }
    except Exception as e:
        return {
            "idx": idx,
            "cmd_str": cmd_str,
            "status": f"error_{str(e)}"
        }

def main():
    solver_path = "/Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/benchmark-size-nine-enumeration/skyscraper_solver"
    filepath = "/Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/benchmark-size-nine-enumeration/benchmark_sets/benchmarkSet9.txt"
    
    print("Step 1: Parsing and deduplicating benchmark set...")
    with open(filepath, 'r') as f:
        lines = [l.strip().strip('"') for l in f if l.strip()]
        
    seen = set()
    unique_instances = []
    for idx, line in enumerate(lines):
        nums = list(map(int, line.split()))
        key = canonize(nums)
        if key not in seen:
            seen.add(key)
            unique_instances.append((idx + 1, line)) # 1-based index to match line number in file
            
    print(f"Total lines in benchmarkSet9.txt: {len(lines)}")
    print(f"Deduplicated unique instances: {len(unique_instances)}")
    
    num_cpus = os.cpu_count() or 4
    print(f"Using {num_cpus} parallel workers.")
    
    # --- PHASE 0: PRE-SCREENING ---
    print("\nStep 2: Pre-screening instances using '-s 1' to sort by difficulty...")
    prescreen_args = [(idx, line, solver_path) for idx, line in unique_instances]
    t_start = time.time()
    with Pool(processes=num_cpus) as pool:
        prescreen_results = pool.map(run_single_sol, prescreen_args)
    t_end = time.time()
    print(f"Pre-screening completed in {t_end - t_start:.2f} seconds.")
    
    # Sort prescreen results by node count
    prescreen_results.sort(key=lambda x: x[2])
    
    print("\nTop 10 easiest instances based on pre-screening:")
    for i in range(min(10, len(prescreen_results))):
        idx, line, nodes, dur = prescreen_results[i]
        print(f"  Line {idx} in file: {nodes} nodes (first sol in {dur:.4f}s)")
        
    # --- PHASE 1-N: ITERATIVE LENGTHENING ---
    # Define rounds: (timeout_seconds, num_candidates_to_try)
    # We will try the easiest candidates first in each round.
    rounds = [
        (0.5, len(prescreen_results)),  # Round 1: try all 1100 unique instances with a 0.5s limit
        (2.0, 500),                    # Round 2: try top 500 easiest remaining with 2.0s limit
        (10.0, 100),                   # Round 3: try top 100 easiest remaining with 10.0s limit
        (60.0, 30),                    # Round 4: try top 30 easiest remaining with 60.0s (1m) limit
        (300.0, 10),                   # Round 5: try top 10 easiest remaining with 300.0s (5m) limit
        (1800.0, 2)                    # Round 6: try top 2 easiest remaining with 1800.0s (30m) limit
    ]
    
    remaining_candidates = [item for item in prescreen_results]
    
    global_start_time = time.time()
    
    for round_idx, (timeout, num_to_try) in enumerate(rounds, 1):
        elapsed_so_far = time.time() - global_start_time
        if elapsed_so_far >= 1800: # 30 mins overall limit
            print(f"\n[LIMIT] Overall time limit of 30 minutes reached. Stopping.")
            break
            
        # Limit num_to_try to available candidates
        to_run = remaining_candidates[:min(num_to_try, len(remaining_candidates))]
        if not to_run:
            print("\nNo candidates left to run.")
            break
            
        print(f"\n--- ROUND {round_idx}: Timeout = {timeout}s, running top {len(to_run)} easiest remaining instances ---")
        
        run_args = [(idx, line, solver_path, timeout) for idx, line, _, _ in to_run]
        
        t_round_start = time.time()
        completed_success = []
        timed_out = []
        
        # We can run in chunks to monitor progress and stop immediately if we find a success
        chunk_size = num_cpus * 4
        with Pool(processes=num_cpus) as pool:
            for chunk_start in range(0, len(run_args), chunk_size):
                if time.time() - global_start_time >= 1800:
                    print("[LIMIT] Overall time limit reached during round.")
                    break
                    
                chunk = run_args[chunk_start : chunk_start + chunk_size]
                chunk_results = pool.map(run_full_enum, chunk)
                
                for r in chunk_results:
                    if r["status"] == "success":
                        completed_success.append(r)
                    elif r["status"] == "timeout":
                        timed_out.append(r["cmd_str"])
                    else:
                        print(f"Instance {r['idx']} failed with status: {r['status']}")
                        
                if completed_success:
                    # We found at least one solvable instance! Let's stop and report.
                    break
                    
        t_round_end = time.time()
        print(f"Round {round_idx} finished in {t_round_end - t_round_start:.2f}s.")
        print(f"Successfully solved under full enumeration in this round: {len(completed_success)}")
        
        if completed_success:
            print("\n🎉 SUCCESS! Found solvable instance(s) under full enumeration!")
            # Sort successes by time or nodes
            completed_success.sort(key=lambda x: x["time"])
            best = completed_success[0]
            print(f"\nBest solvable instance details:")
            print(f"  Line in benchmarkSet9.txt: {best['idx']}")
            print(f"  Constraints string: \"{best['cmd_str']}\"")
            print(f"  Time taken: {best['time']:.4f} seconds")
            print(f"  Nodes visited: {best['nodes']}")
            print(f"  Solutions found: {best['sols_found']}")
            print(f"\nSolver output:\n")
            print(best["stdout"])
            
            # Save the results to an artifact or output file
            with open("solvable_size9_instance.txt", "w") as out_f:
                out_f.write(f"Line: {best['idx']}\n")
                out_f.write(f"Constraints: \"{best['cmd_str']}\"\n")
                out_f.write(f"Time: {best['time']:.4f}s\n")
                out_f.write(f"Nodes: {best['nodes']}\n")
                out_f.write(f"Solutions: {best['sols_found']}\n\n")
                out_f.write(best["stdout"])
            return
            
        # Update remaining candidates for next round
        # Only keep candidates that timed out in this round (since any that had errors or other issues are discarded)
        timed_out_set = set(timed_out)
        remaining_candidates = [c for c in remaining_candidates if c[1] in timed_out_set]
        print(f"Remaining candidates for next rounds: {len(remaining_candidates)}")
        
    print("\nCould not find any solvable size 9 instance under full enumeration within the time budget.")

if __name__ == "__main__":
    main()
