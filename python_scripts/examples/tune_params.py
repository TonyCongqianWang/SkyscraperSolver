#!/usr/bin/env python3
import subprocess
import re
import sys
import os

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
    print(f"Testing: G_SEL_REBUILD_PERIOD={sel_period}, G_PRUNE_PERIOD_SHALLOW={prune_period}, G_MIN_UNSET_R_PRUNE={min_unset}")
    
    # Recompile
    cflags = f"-Wall -Wextra -Werror -O2 -DG_SEL_REBUILD_PERIOD={sel_period} -DG_PRUNE_PERIOD_SHALLOW={prune_period} -DG_MIN_UNSET_R_PRUNE={min_unset}"
    ret, out, err = run_cmd(f"make clean && make CFLAGS='{cflags}'")
    if ret != 0:
        print(f"Compilation failed: {err}")
        return None
        
    # Run benchmark
    bench_cmd = "python3 python_scripts/run_benchmark.py benchmark_sets/benchmarkSet8_easy50.txt -f '-s 0' --print-time-period 0"
    ret, out, err = run_cmd(bench_cmd)
    if ret != 0:
        print(f"Benchmark failed: {err}")
        return None
        
    total_time, total_nodes = parse_benchmark_summary(out)
    print(f"  Result -> Nodes: {total_nodes:,}, Time: {total_time:.3f}s")
    return total_time, total_nodes

def main():
    configs = [
        (4, 80, 0.5),
        (4, 160, 0.5),
        (4, 320, 0.5),
        (8, 80, 0.5),
        (8, 160, 0.5),
        (8, 320, 0.5),
        (4, 80, 0.6),
        (4, 160, 0.6),
        (8, 80, 0.6),
        (8, 160, 0.6)
    ]
    
    best_nodes = float('inf')
    best_time = float('inf')
    best_config = None
    
    results = []
    for sel, prune, min_u in configs:
        res = test_config(sel, prune, min_u)
        if res:
            t, n = res
            results.append((sel, prune, min_u, n, t))
            if n < best_nodes:
                best_nodes = n
                best_time = t
                best_config = (sel, prune, min_u)
                
    print("\n=== SWEEP RESULTS ===")
    for sel, prune, min_u, n, t in results:
        print(f"SEL={sel}, PRUNE={prune}, MIN_UNSET={min_u} -> Nodes: {n:,}, Time: {t:.3f}s")
        
    print(f"\nBest Config by Nodes: SEL={best_config[0]}, PRUNE={best_config[1]}, MIN_UNSET={best_config[2]} (Nodes: {best_nodes:,}, Time: {best_time:.3f}s)")

if __name__ == "__main__":
    main()
