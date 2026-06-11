#!/usr/bin/env python3
import subprocess
import time
import sys
import concurrent.futures

def run_cmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr

def run_solver(binary, options, clues):
    cmd = [binary] + options.split() + [clues]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate()
        nodes = 0
        for line in stdout.splitlines():
            if line.startswith("Nodes visited:"):
                nodes = int(line.split(":")[1].strip())
        return nodes
    except Exception:
        return 0

def benchmark_parallel(binary, options, benchmark_file, workers=4):
    with open(benchmark_file, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
    total_nodes = 0
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_solver, binary, options, line) for line in lines]
        for fut in concurrent.futures.as_completed(futures):
            total_nodes += fut.result()
    elapsed = time.time() - start_time
    return total_nodes, elapsed

def test_config(sel_period, prune_period, min_unset, benchmark_file, options, workers=4):
    # Recompile C solver
    cflags = f"-Wall -Wextra -Werror -O2 -DG_SEL_REBUILD_PERIOD={sel_period} -DG_PRUNE_PERIOD_SHALLOW={prune_period} -DG_MIN_UNSET_R_PRUNE={min_unset}"
    ret, out, err = run_cmd(f"make clean && make CFLAGS='{cflags}'")
    if ret != 0:
        return None
    # Run parallel benchmark
    return benchmark_parallel("./skyscraper_solver", options, benchmark_file, workers)

def main():
    top_10 = [
        (2, 120, 0.5),
        (2, 80, 0.5),
        (4, 80, 0.5),
        (2, 160, 0.5),
        (4, 160, 0.5),
        (8, 120, 0.5),
        (2, 120, 0.45),
        (2, 40, 0.5),
        (4, 40, 0.5),
        (4, 120, 0.45)
    ]
    
    print("=== STARTING FULL VALIDATION (PARALLEL WORKERS = 4) ===")
    
    # Let's first benchmark the baseline (skyscraper_solver_main)
    print("\n[Baseline] Benchmarking skyscraper_solver_main on size 8 (single solution)...")
    base8_nodes, base8_time = benchmark_parallel("./skyscraper_solver_main", "-s 1", "benchmark_sets/benchmarkSet8.txt")
    print(f"  Result -> Nodes: {base8_nodes:,}, Time: {base8_time:.3f}s")
    
    print("\n[Baseline] Benchmarking skyscraper_solver_main on size 7 (all solutions)...")
    base7_nodes, base7_time = benchmark_parallel("./skyscraper_solver_main", "-s 0", "benchmark_sets/benchmarkSet7.txt")
    print(f"  Result -> Nodes: {base7_nodes:,}, Time: {base7_time:.3f}s")
    
    # Benchmark Step 1 (default config: SEL=160, PRUNE=160, MIN_UNSET=0.4)
    print("\n[Step 1] Benchmarking un-tuned C solver on size 8 (single solution)...")
    s1_8_res = test_config(160, 160, 0.4, "benchmark_sets/benchmarkSet8.txt", "-s 1")
    s1_8_nodes, s1_8_time = s1_8_res if s1_8_res else (0, 0)
    print(f"  Result -> Nodes: {s1_8_nodes:,}, Time: {s1_8_time:.3f}s")
    
    print("\n[Step 1] Benchmarking un-tuned C solver on size 7 (all solutions)...")
    s1_7_res = test_config(160, 160, 0.4, "benchmark_sets/benchmarkSet7.txt", "-s 0")
    s1_7_nodes, s1_7_time = s1_7_res if s1_7_res else (0, 0)
    print(f"  Result -> Nodes: {s1_7_nodes:,}, Time: {s1_7_time:.3f}s")
    
    print("\nEvaluating top 10 configurations...")
    results_s8 = []
    results_s7 = []
    
    for i, (sel, prune, min_u) in enumerate(top_10, 1):
        print(f"\n[{i}/10] Testing SEL={sel}, PRUNE={prune}, MIN_UNSET={min_u}...")
        
        # Run size 8
        res_8 = test_config(sel, prune, min_u, "benchmark_sets/benchmarkSet8.txt", "-s 1")
        if res_8:
            n_8, t_8 = res_8
            results_s8.append((sel, prune, min_u, n_8, t_8))
            print(f"  Size 8 (-s 1) -> Nodes: {n_8:,}, Time: {t_8:.3f}s")
            
        # Run size 7
        res_7 = test_config(sel, prune, min_u, "benchmark_sets/benchmarkSet7.txt", "-s 0")
        if res_7:
            n_7, t_7 = res_7
            results_s7.append((sel, prune, min_u, n_7, t_7))
            print(f"  Size 7 (-s 0) -> Nodes: {n_7:,}, Time: {t_7:.3f}s")
            
    # Print comparison
    print("\n=== RANKING FOR SIZE 8 (-s 1) ===")
    sorted_s8 = sorted(results_s8, key=lambda x: x[3])
    for rank, (sel, prune, min_u, n, t) in enumerate(sorted_s8, 1):
        diff_nodes = (n - base8_nodes) / base8_nodes * 100
        diff_time = (t - base8_time) / base8_time * 100
        print(f"{rank}. SEL={sel}, PRUNE={prune}, MIN_UNSET={min_u} -> Nodes: {n:,} ({diff_nodes:+.2f}%), Time: {t:.3f}s ({diff_time:+.2f}%)")
        
    print("\n=== RANKING FOR SIZE 7 (-s 0) ===")
    sorted_s7 = sorted(results_s7, key=lambda x: x[3])
    for rank, (sel, prune, min_u, n, t) in enumerate(sorted_s7, 1):
        diff_nodes = (n - base7_nodes) / base7_nodes * 100
        diff_time = (t - base7_time) / base7_time * 100
        print(f"{rank}. SEL={sel}, PRUNE={prune}, MIN_UNSET={min_u} -> Nodes: {n:,} ({diff_nodes:+.2f}%), Time: {t:.3f}s ({diff_time:+.2f}%)")

if __name__ == "__main__":
    main()
