#!/usr/bin/env python3
import subprocess
import re
import sys
import os
import time

def run_cmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr

def parse_benchmark_summary(stdout):
    total_time = 0.0
    total_nodes = 0
    for line in stdout.splitlines():
        if line.startswith("Total:"):
            # Could be time or nodes. Let's parse both
            parts = line.split(":")
            if len(parts) == 4: # hh:mm:ss
                try:
                    h, m, s = float(parts[1]), float(parts[2]), float(parts[3])
                    total_time = h * 3600 + m * 60 + s
                except ValueError:
                    pass
            else: # Total nodes
                try:
                    total_nodes = int(parts[1].strip().replace(",", ""))
                except ValueError:
                    pass
    return total_time, total_nodes

def test_config(sel_period, prune_period, min_unset):
    # Recompile
    cflags = f"-Wall -Wextra -Werror -O2 -DG_SEL_REBUILD_PERIOD={sel_period} -DG_PRUNE_PERIOD_SHALLOW={prune_period} -DG_MIN_UNSET_R_PRUNE={min_unset}"
    ret, out, err = run_cmd(f"make clean && make CFLAGS='{cflags}'")
    if ret != 0:
        return None
        
    # Run benchmark
    bench_cmd = "python3 python_scripts/run_benchmark.py benchmark_sets/benchmarkSet8_easy50.txt -f '-s 0' --print-time-period 0"
    ret, out, err = run_cmd(bench_cmd)
    if ret != 0:
        return None
        
    total_time, total_nodes = parse_benchmark_summary(out)
    return total_time, total_nodes

def main():
    sel_periods = [2, 4, 8, 12, 16, 32, 64, 160]
    prune_periods = [40, 80, 120, 160, 240, 320]
    min_unsets = [0.4, 0.45, 0.5, 0.55, 0.6]
    
    total_configs = len(sel_periods) * len(prune_periods) * len(min_unsets)
    print(f"Starting Grid Search of {total_configs} configurations...")
    print(f"Sweep space:")
    print(f"  G_SEL_REBUILD_PERIOD: {sel_periods}")
    print(f"  G_PRUNE_PERIOD_SHALLOW: {prune_periods}")
    print(f"  G_MIN_UNSET_R_PRUNE: {min_unsets}")
    print("-" * 60)
    
    best_nodes = float('inf')
    best_time = float('inf')
    best_config = None
    
    results = []
    start_time = time.time()
    
    count = 0
    for sel in sel_periods:
        for prune in prune_periods:
            for min_u in min_unsets:
                count += 1
                res = test_config(sel, prune, min_u)
                if res:
                    t, n = res
                    results.append((sel, prune, min_u, n, t))
                    if n < best_nodes:
                        best_nodes = n
                        best_time = t
                        best_config = (sel, prune, min_u)
                    
                    # Print periodic status
                    elapsed = time.time() - start_time
                    avg_time = elapsed / count
                    eta = avg_time * (total_configs - count)
                    print(f"Config {count}/{total_configs} (SEL={sel}, PRUNE={prune}, MIN_UNSET={min_u}) -> Nodes: {n:,}, Time: {t:.3f}s | Elapsed: {elapsed/60:.1f}m, ETA: {eta/60:.1f}m")
                else:
                    print(f"Config {count}/{total_configs} (SEL={sel}, PRUNE={prune}, MIN_UNSET={min_u}) -> FAILED")
                sys.stdout.flush()
                
    print("\n=== SWEEP RESULTS ===")
    # Print top 20 configurations sorted by node count
    sorted_results = sorted(results, key=lambda x: x[3])
    print("Top 20 configurations:")
    for sel, prune, min_u, n, t in sorted_results[:20]:
        print(f"SEL={sel}, PRUNE={prune}, MIN_UNSET={min_u} -> Nodes: {n:,}, Time: {t:.3f}s")
        
    print(f"\nBest Config by Nodes: SEL={best_config[0]}, PRUNE={best_config[1]}, MIN_UNSET={best_config[2]} (Nodes: {best_nodes:,}, Time: {best_time:.3f}s)")

if __name__ == "__main__":
    main()
