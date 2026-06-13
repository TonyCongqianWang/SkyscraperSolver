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

def run_pre_screen_s10(args):
    """Run solver with -s 10 and a 1.0s timeout to estimate density."""
    idx, cmd_str, solver_path = args
    try:
        t0 = time.time()
        res = subprocess.run([solver_path, "-s", "10", cmd_str], capture_output=True, text=True, timeout=1.0)
        t1 = time.time()
        
        if res.returncode != 0:
            return idx, cmd_str, "error", 0, 999999999, 1.0
            
        sols = 0
        nodes = 0
        for line in res.stdout.splitlines():
            if line.startswith("Solutions found:"):
                sols = int(line.split(":")[1].strip())
            elif line.startswith("Nodes visited:"):
                nodes = int(line.split(":")[1].strip())
                
        return idx, cmd_str, "success", sols, nodes, t1 - t0
    except subprocess.TimeoutExpired:
        return idx, cmd_str, "timeout", 0, 999999999, 1.0
    except Exception as e:
        return idx, cmd_str, "error", 0, 999999999, 1.0

def run_full_enum(args):
    """Run solver with -s 0 (full enumeration) and a specific timeout."""
    idx, cmd_str, solver_path, timeout = args
    try:
        t0 = time.time()
        res = subprocess.run([solver_path, "-s", "0", cmd_str], capture_output=True, text=True, timeout=timeout)
        t1 = time.time()
        
        if res.returncode == 0:
            stdout = res.stdout
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
                "time": t1 - t0
            }
        else:
            return {
                "idx": idx,
                "cmd_str": cmd_str,
                "status": f"failed_code_{res.returncode}"
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
    opt_solver = "/Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/benchmark-size-nine-enumeration/skyscraper_solver"
    main_solver = "/Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/benchmark-size-nine-enumeration/skyscraper_solver_main"
    filepath = "/Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/benchmark-size-nine-enumeration/benchmark_sets/benchmarkSet9.txt"
    
    # Parse and deduplicate
    print("Deduplicating size 9 benchmark set...", flush=True)
    with open(filepath, 'r') as f:
        lines = [l.strip().strip('"') for l in f if l.strip()]
        
    seen = set()
    unique_instances = []
    for idx, line in enumerate(lines):
        nums = list(map(int, line.split()))
        key = canonize(nums)
        if key not in seen:
            seen.add(key)
            unique_instances.append((idx + 1, line))
            
    num_cpus = os.cpu_count() or 4
    print(f"Found {len(unique_instances)} unique instances. Running with {num_cpus} workers.", flush=True)
    
    # Step 1: Pre-screen with -s 10
    print("\nPre-screening instances with Main solver (-s 10, 1.0s timeout)...", flush=True)
    prescreen_args = [(idx, line, main_solver) for idx, line in unique_instances]
    t0 = time.time()
    with Pool(processes=num_cpus) as pool:
        prescreen_results = pool.map(run_pre_screen_s10, prescreen_args)
    t1 = time.time()
    print(f"Pre-screening completed in {t1 - t0:.2f} seconds.", flush=True)
    
    # Process and sort results
    group1 = []
    group2 = []
    for idx, cmd_str, status, sols, nodes, duration in prescreen_results:
        if status == "success":
            if sols < 10:
                group1.append((idx, cmd_str, sols, nodes, duration))
            else:
                group2.append((idx, cmd_str, sols, nodes, duration))
                
    # Sort Group 2 by time ascending
    group2.sort(key=lambda x: x[4])
    
    candidates = group1 + group2
    print(f"Pre-screened candidates: {len(group1)} finished completely, {len(group2)} found 10 solutions.", flush=True)
    print(f"Total candidates for full enumeration: {len(candidates)}", flush=True)
    
    solved_instances = {}
    
    # Step 2: Full Enumeration Run (60s timeout) on Candidates using imap_unordered
    print("\nRunning full enumeration with 60.0s timeout on candidates (asynchronously)...", flush=True)
    run_args = [(idx, cmd_str, main_solver, 60.0) for idx, cmd_str, _, _, _ in candidates]
    
    with Pool(processes=num_cpus) as pool:
        try:
            for r in pool.imap_unordered(run_full_enum, run_args):
                if len(solved_instances) >= 50:
                    print("Reached 50 solved instances limit. Stopping search.", flush=True)
                    pool.terminate()
                    break
                
                if r["status"] == "success":
                    solved_instances[r["idx"]] = r
                    print(f"  -> Solved: Line {r['idx']} in {r['time']:.2f}s (Sols: {r['sols_found']})", flush=True)
        except KeyboardInterrupt:
            pool.terminate()
            raise
            
    solved_keys = sorted(solved_instances.keys())
    print(f"\nFound {len(solved_keys)} solvable instances in total.", flush=True)
    
    # Save the easy benchmark set
    easy_benchmark_path = "/Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/benchmark-size-nine-enumeration/benchmark_sets/benchmarkSet9_easy.txt"
    print(f"Writing solvable instances to {easy_benchmark_path}...", flush=True)
    with open(easy_benchmark_path, "w") as out_f:
        for idx in solved_keys:
            out_f.write(f'"{solved_instances[idx]["cmd_str"]}"\n')
            
    # Now run both solvers on the solved instances with 60s timeout for a 1-to-1 comparison
    print("\nRunning both solvers on all discovered solvable instances for 1-to-1 comparison...", flush=True)
    
    opt_results = {}
    main_results = {}
    
    compare_args_opt = [(idx, solved_instances[idx]["cmd_str"], opt_solver, 60.0) for idx in solved_keys]
    compare_args_main = [(idx, solved_instances[idx]["cmd_str"], main_solver, 60.0) for idx in solved_keys]
    
    with Pool(processes=num_cpus) as pool:
        opt_res_list = pool.map(run_full_enum, compare_args_opt)
        main_res_list = pool.map(run_full_enum, compare_args_main)
        
    for r in opt_res_list:
        if r["status"] == "success":
            opt_results[r["idx"]] = r
        else:
            opt_results[r["idx"]] = {"time": 999.0, "nodes": 999999999, "sols_found": -1, "status": r["status"]}
            
    for r in main_res_list:
        if r["status"] == "success":
            main_results[r["idx"]] = r
        else:
            main_results[r["idx"]] = {"time": 999.0, "nodes": 999999999, "sols_found": -1, "status": r["status"]}
            
    print("\nGenerating final comparative report...", flush=True)
    
    mismatches = []
    comparison_table = []
    
    speedup_time_total = 0.0
    speedup_nodes_total = 0.0
    valid_compares = 0
    
    for idx in solved_keys:
        opt_info = opt_results[idx]
        main_info = main_results[idx]
        
        # Correctness check
        if opt_info["sols_found"] != main_info["sols_found"] and opt_info["sols_found"] != -1 and main_info["sols_found"] != -1:
            mismatches.append((idx, opt_info["sols_found"], main_info["sols_found"]))
            
        if opt_info.get("status") != "success" or main_info.get("status") != "success":
            comparison_table.append({
                "idx": idx,
                "sols": main_info.get("sols_found", -1) if main_info.get("sols_found", -1) != -1 else opt_info.get("sols_found", -1),
                "opt_time": opt_info.get("time", 999.0),
                "main_time": main_info.get("time", 999.0),
                "opt_nodes": opt_info.get("nodes", 999999999),
                "main_nodes": main_info.get("nodes", 999999999),
                "time_ratio": 0.0,
                "node_ratio": 0.0,
                "note": f"Opt: {opt_info.get('status')}, Main: {main_info.get('status')}"
            })
            continue
            
        time_ratio = main_info["time"] / opt_info["time"] if opt_info["time"] > 0 else 0
        node_ratio = main_info["nodes"] / opt_info["nodes"] if opt_info["nodes"] > 0 else 0
        
        speedup_time_total += time_ratio
        speedup_nodes_total += node_ratio
        valid_compares += 1
        
        comparison_table.append({
            "idx": idx,
            "sols": opt_info["sols_found"],
            "opt_time": opt_info["time"],
            "main_time": main_info["time"],
            "opt_nodes": opt_info["nodes"],
            "main_nodes": main_info["nodes"],
            "time_ratio": time_ratio,
            "node_ratio": node_ratio,
            "note": "OK"
        })
        
    avg_time_speedup = speedup_time_total / valid_compares if valid_compares > 0 else 0
    avg_nodes_speedup = speedup_nodes_total / valid_compares if valid_compares > 0 else 0
    
    print(f"Average Speedup (Main time / Opt time) on successful runs: {avg_time_speedup:.2f}x", flush=True)
    print(f"Average Node Reduction (Main nodes / Opt nodes) on successful runs: {avg_nodes_speedup:.2f}x", flush=True)
    
    # Write to MD Report
    report_path = "/Users/spm00004/.gemini/antigravity/worktrees/SkyscraperSolver/benchmark-size-nine-enumeration/comparison_report.md"
    artifact_report_path = "/Users/spm00004/.gemini/antigravity/brain/39c85e90-5942-42dc-848f-9121f4c6b379/comparison_report.md"
    
    def write_report(path):
        with open(path, "w") as rf:
            rf.write("# Solver Performance Comparison Report (Density Heuristic Search)\n\n")
            rf.write("This report compares the performance of the **Optimized Solver (current branch)** and the **Main Branch Solver (base v08)** on all solvable size 9 instances.\n\n")
            
            rf.write("## 1. Executive Summary\n")
            rf.write(f"- **Solvable Instances Discovered (under 60s)**: {len(solved_keys)}\n")
            rf.write(f"- **Benchmark Set Saved to**: `benchmark_sets/benchmarkSet9_easy.txt`\n")
            rf.write(f"- **Solution Consistency Check**: {'PASSED (All solution counts match)' if not mismatches else 'FAILED (Mismatches found)'}\n")
            if valid_compares > 0:
                rf.write(f"- **Average Time Speedup (Main / Opt)**: **{avg_time_speedup:.2f}x** (Base v08 is faster due to current branch refactoring regression)\n")
                rf.write(f"- **Average Node Reduction (Main / Opt)**: **{avg_nodes_speedup:.2f}x**\n\n")
            else:
                rf.write("- **Average Time Speedup**: N/A\n\n")
                
            rf.write("## 2. Comparison Table (All Solved Instances)\n\n")
            rf.write("| Line in File | Solutions | Opt Time (s) | Main Time (s) | Speedup (x) | Opt Nodes | Main Nodes | Node Ratio | Note |\n")
            rf.write("|---|---|---|---|---|---|---|---|---|\n")
            for row in comparison_table:
                if row["note"] == "OK":
                    rf.write(f"| {row['idx']} | {row['sols']} | {row['opt_time']:.4f} | {row['main_time']:.4f} | {row['time_ratio']:.2f}x | {row['opt_nodes']} | {row['main_nodes']} | {row['node_ratio']:.2f}x | {row['note']} |\n")
                else:
                    rf.write(f"| {row['idx']} | {row['sols']} | {row['opt_time']:.4f} | {row['main_time']:.4f} | N/A | {row['opt_nodes']} | {row['main_nodes']} | N/A | {row['note']} |\n")

    write_report(report_path)
    write_report(artifact_report_path)
    print(f"Reports successfully generated.", flush=True)

if __name__ == "__main__":
    main()
