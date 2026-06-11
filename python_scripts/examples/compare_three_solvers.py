#!/usr/bin/env python3
import subprocess
import sys
import time

def run_cmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr

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

def run_set(benchmark_file, options):
    with open(benchmark_file, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    results = {
        "base": {"nodes": 0, "time": 0.0},
        "step1": {"nodes": 0, "time": 0.0},
        "step2": {"nodes": 0, "time": 0.0}
    }
    
    for idx, clues in enumerate(lines, start=1):
        res_base = run_solver("./skyscraper_solver_main", options, clues)
        res_step1 = run_solver("./skyscraper_solver_step1", options, clues)
        res_step2 = run_solver("./skyscraper_solver", options, clues)
        
        if "error" in res_base or "error" in res_step1 or "error" in res_step2:
            continue
            
        results["base"]["nodes"] += res_base["nodes"]
        results["base"]["time"] += res_base["time"]
        
        results["step1"]["nodes"] += res_step1["nodes"]
        results["step1"]["time"] += res_step1["time"]
        
        results["step2"]["nodes"] += res_step2["nodes"]
        results["step2"]["time"] += res_step2["time"]
        
    return results

def main():
    print("Recompiling Step 2 solver with default parameters...")
    run_cmd("make clean")
    code, out, err = run_cmd("make")
    if code != 0:
        print(f"Compilation failed: {err}")
        sys.exit(1)
    print("Compilation successful.")
    print("-" * 80)
    
    print("Running complete Size 7 Benchmark (6,000 instances, exhaustive -s 0)...")
    res7 = run_set("benchmark_sets/benchmarkSet7.txt", "-s 0")
    
    base_n7, base_t7 = res7["base"]["nodes"], res7["base"]["time"]
    step1_n7, step1_t7 = res7["step1"]["nodes"], res7["step1"]["time"]
    step2_n7, step2_t7 = res7["step2"]["nodes"], res7["step2"]["time"]
    
    print(f"Size 7 Nodes: Base={base_n7}, Step1={step1_n7} (Red={(base_n7-step1_n7)/base_n7*100:.2f}%), Step2={step2_n7} (Red={(base_n7-step2_n7)/base_n7*100:.2f}%)")
    print(f"Size 7 Time:  Base={base_t7:.3f}s, Step1={step1_t7:.3f}s (Speedup={(base_t7-step1_t7)/base_t7*100:.2f}%), Step2={step2_t7:.3f}s (Speedup={(base_t7-step2_t7)/base_t7*100:.2f}%)")
    print("-" * 80)
    
    print("Running complete Size 8 Benchmark (6,000 instances, single solution -s 1)...")
    res8 = run_set("benchmark_sets/benchmarkSet8.txt", "-s 1")
    
    base_n8, base_t8 = res8["base"]["nodes"], res8["base"]["time"]
    step1_n8, step1_t8 = res8["step1"]["nodes"], res8["step1"]["time"]
    step2_n8, step2_t8 = res8["step2"]["nodes"], res8["step2"]["time"]
    
    print(f"Size 8 Nodes: Base={base_n8}, Step1={step1_n8} (Red={(base_n8-step1_n8)/base_n8*100:.2f}%), Step2={step2_n8} (Red={(base_n8-step2_n8)/base_n8*100:.2f}%)")
    print(f"Size 8 Time:  Base={base_t8:.3f}s, Step1={step1_t8:.3f}s (Speedup={(base_t8-step1_t8)/base_t8*100:.2f}%), Step2={step2_t8:.3f}s (Speedup={(base_t8-step2_t8)/base_t8*100:.2f}%)")
    print("-" * 80)

if __name__ == "__main__":
    main()
