#!/usr/bin/env python3
import subprocess
import os
import time
import concurrent.futures
import math

# Benchmark files
SET_A = "benchmark_sets/benchmarkSet8.txt"                 # 6000 instances, -s 1
SET_B = "benchmark_sets/benchmarkSet8_subset100.txt"        # 100 instances, -s 0
SET_C = "benchmark_sets/benchmarkSet9_subset300.txt"        # 300 instances, -s 1

# Workers for evaluation
WORKERS = 8

def load_instances(filepath):
    with open(filepath) as f:
        return [l.strip().strip('"') for l in f if l.strip()]

def run_solver(binary, env, opt, clue, timeout):
    t_start = time.time()
    try:
        r = subprocess.run(
            [binary] + opt.split() + [clue],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=timeout, env=env)
        elapsed = time.time() - t_start
        if r.returncode != 0:
            return None
        for line in r.stdout.splitlines():
            if line.startswith("Nodes visited:"):
                return int(line.split(":")[1].strip()), elapsed
    except Exception:
        pass
    return None

def shifted_geo_mean(values, shift):
    if not values:
        return 0.0
    sum_ln = sum(math.log(max(0.0, float(x)) + shift) for x in values)
    return math.exp(sum_ln / len(values)) - shift

def evaluate_config(binary, env, instances, opt, timeout):
    nodes_list = []
    times_list = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(run_solver, binary, env, opt, clue, timeout) for clue in instances]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res is None:
                return None
            nodes, elapsed = res
            nodes_list.append(nodes)
            times_list.append(elapsed)
            
    # Calculate stats
    sum_nodes = sum(nodes_list)
    sum_times = sum(times_list)
    
    sgm_nodes = shifted_geo_mean(nodes_list, 1000.0)
    sgm_times = shifted_geo_mean(times_list, 0.1)
    
    return {
        "sum_nodes": sum_nodes,
        "sum_times": sum_times,
        "mean_nodes": sum_nodes / len(instances) if instances else 0.0,
        "mean_times": sum_times / len(instances) if instances else 0.0,
        "sgm_nodes": sgm_nodes,
        "sgm_times": sgm_times
    }


def main():
    print("Rebuilding solver with env support...")
    subprocess.run("make clean && make CFLAGS=\"-Wall -Wextra -Werror -O2 -DG_PRUNE_NO_ENV=0\"", shell=True, stdout=subprocess.DEVNULL)
    # Copy skyscraper_solver to skyscraper_solver_env
    if os.path.exists("skyscraper_solver_env"):
        os.remove("skyscraper_solver_env")
    os.rename("skyscraper_solver", "skyscraper_solver_env")

    # Rebuild default version to restore clean environment
    subprocess.run("make clean && make", shell=True, stdout=subprocess.DEVNULL)

    s8_full = load_instances(SET_A)
    s8_100 = load_instances(SET_B)
    s9_300 = load_instances(SET_C)
    s8_easy = load_instances("benchmark_sets/benchmarkSet8_easy50.txt")

    # Top 10 configurations from sweep + baseline
    configs = [
        ("baseline_main", None),
        ("idx=7354 (V4 winner)", ("0.56", "340", "50", "1", "4", "0.53", "0.2", "0.5", "1.0", "0")),
        ("idx=6165", ("0.54", "360", "120", "1", "3", "0.50", "1.0", "0.5", "0.1", "0")),
        ("idx=7609", ("0.56", "360", "50", "1", "3", "0.53", "0.2", "0.5", "1.0", "0")),
        ("idx=7381", ("0.56", "340", "60", "1", "3", "0.50", "0.2", "0.5", "1.0", "0")),
        ("idx=7170", ("0.56", "220", "80", "1", "4", "0.50", "1.0", "0.5", "0.1", "0")),
        ("idx=8790", ("0.58", "220", "80", "1", "4", "0.50", "1.0", "0.5", "0.1", "0")),
        ("idx=7576", ("0.56", "360", "40", "1", "4", "0.50", "0.2", "0.5", "1.0", "0")),
        ("idx=6990", ("0.56", "200", "120", "1", "4", "0.50", "1.0", "0.5", "0.1", "0")),
        ("idx=7561", ("0.56", "360", "40", "1", "3", "0.50", "0.2", "0.5", "1.0", "0")),
        ("idx=9016", ("0.58", "340", "60", "1", "4", "0.50", "0.2", "0.5", "1.0", "0"))
    ]

    # ── SMOKE TEST ──
    print("\nRunning Quick Smoke Test to check for infinite loops...")
    smoke_s8_easy = s8_easy[:5]
    smoke_s9_300 = s9_300[:5]
    
    for name, params in configs:
        if name == "baseline_main":
            binary = "./skyscraper_solver_main"
            env = os.environ.copy()
        else:
            binary = "./skyscraper_solver_env"
            min_u, shal, deep, th0, th1, gac, lin, quad, cubic, kp = params
            env = os.environ.copy()
            env["G_MIN_UNSET_R_PRUNE"] = min_u
            env["G_PRUNE_PERIOD_SHALLOW"] = shal
            env["G_PRUNE_EXTRA_PERIOD_DEEP"] = deep
            env["G_PRUNE_DEPTH_THRESHOLD_0"] = th0
            env["G_PRUNE_DEPTH_THRESHOLD_1"] = th1
            env["G_PRUNE_GAC_UNSET_R_THRESHOLD"] = gac
            env["G_PRUNE_LIN_COEFF"] = lin
            env["G_PRUNE_QUAD_COEFF"] = quad
            env["G_PRUNE_CUBIC_COEFF"] = cubic
            env["KEEP_PRUNING"] = kp
            
        print(f"  Testing {name}...")
        # Evaluate with a 10s timeout
        res_s8 = evaluate_config(binary, env, smoke_s8_easy, "-s 0", 10.0)
        res_s9 = evaluate_config(binary, env, smoke_s9_300, "-s 1", 10.0)
        
        if res_s8 is None or res_s9 is None:
            print(f"  [ERROR] Smoke test failed for {name}! Possible infinite loop or solver crash.")
            return

    print("Smoke test PASSED! Proceeding to the full validation sweep.\n")

    print("Starting Validation Sweep...")
    print(f"Set A (size8full):  {len(s8_full)} instances, single solution (-s 1)")
    print(f"Set B (size8_100):   {len(s8_100)} instances, all solutions (-s 0)")
    print(f"Set C (size9_300):   {len(s9_300)} instances, single solution (-s 1)")
    print("=" * 100)

    results = []

    for name, params in configs:
        print(f"\nEvaluating: {name}...")
        
        if name == "baseline_main":
            binary = "./skyscraper_solver_main"
            env = os.environ.copy()
        else:
            binary = "./skyscraper_solver_env"
            min_u, shal, deep, th0, th1, gac, lin, quad, cubic, kp = params
            env = os.environ.copy()
            env["G_MIN_UNSET_R_PRUNE"] = min_u
            env["G_PRUNE_PERIOD_SHALLOW"] = shal
            env["G_PRUNE_EXTRA_PERIOD_DEEP"] = deep
            env["G_PRUNE_DEPTH_THRESHOLD_0"] = th0
            env["G_PRUNE_DEPTH_THRESHOLD_1"] = th1
            env["G_PRUNE_GAC_UNSET_R_THRESHOLD"] = gac
            env["G_PRUNE_LIN_COEFF"] = lin
            env["G_PRUNE_QUAD_COEFF"] = quad
            env["G_PRUNE_CUBIC_COEFF"] = cubic
            env["KEEP_PRUNING"] = kp

        # Run Set A - Timeout: 10s
        print("  Running Set A (size8full, -s 1)...")
        res_a = evaluate_config(binary, env, s8_full, "-s 1", 10.0)
        if res_a:
            print(f"    Set A Finished: Sum Nodes = {res_a['sum_nodes']:,}, Mean Nodes = {res_a['mean_nodes']:.1f}, SGM Nodes = {int(res_a['sgm_nodes']):,}, Sum Time = {res_a['sum_times']:.2f}s, Mean Time = {res_a['mean_times']:.3f}s, SGM Time = {res_a['sgm_times']:.3f}s")
        else:
            print("    Set A FAILED (Timeout or Error)")
        
        # Run Set B - Timeout: 5400s (1.5h)
        print("  Running Set B (size8_100, -s 0)...")
        res_b = evaluate_config(binary, env, s8_100, "-s 0", 5400.0)
        if res_b:
            print(f"    Set B Finished: Sum Nodes = {res_b['sum_nodes']:,}, Mean Nodes = {res_b['mean_nodes']:.1f}, SGM Nodes = {int(res_b['sgm_nodes']):,}, Sum Time = {res_b['sum_times']:.2f}s, Mean Time = {res_b['mean_times']:.3f}s, SGM Time = {res_b['sgm_times']:.3f}s")
        else:
            print("    Set B FAILED (Timeout or Error)")
        
        # Run Set C - Timeout: 5400s (1.5h)
        print("  Running Set C (size9_300, -s 1)...")
        res_c = evaluate_config(binary, env, s9_300, "-s 1", 5400.0)
        if res_c:
            print(f"    Set C Finished: Sum Nodes = {res_c['sum_nodes']:,}, Mean Nodes = {res_c['mean_nodes']:.1f}, SGM Nodes = {int(res_c['sgm_nodes']):,}, Sum Time = {res_c['sum_times']:.2f}s, Mean Time = {res_c['mean_times']:.3f}s, SGM Time = {res_c['sgm_times']:.3f}s")
        else:
            print("    Set C FAILED (Timeout or Error)")

        results.append({
            "name": name,
            "res_a": res_a,
            "res_b": res_b,
            "res_c": res_c
        })

    # Print Report
    print("\n\n" + "=" * 100)
    print("FINAL VALIDATION SWEEP REPORT")
    print("=" * 100)
    
    # Report Set A
    print("\n### Set A: size8full (6000 instances, single solution -s 1)")
    print(f"{'Configuration':<25} | {'Sum Nodes':<18} | {'SGM Nodes (s=1k)':<18} | {'Sum Time':<12} | {'SGM Time (s=0.1)':<18}")
    print("-" * 100)
    for r in results:
        res = r["res_a"]
        if res:
            print(f"{r['name']:<25} | {res['sum_nodes']:<18,} | {int(res['sgm_nodes']):<18,} | {res['sum_times']:<10.2f}s | {res['sgm_times']:<15.3f}s")
        else:
            print(f"{r['name']:<25} | {'FAILED':<18} | {'N/A':<18} | {'N/A':<12} | {'N/A':<18}")

    # Report Set B
    print("\n### Set B: size8_100 (100 instances, all solutions -s 0)")
    print(f"{'Configuration':<25} | {'Sum Nodes':<18} | {'SGM Nodes (s=1k)':<18} | {'Sum Time':<12} | {'SGM Time (s=0.1)':<18}")
    print("-" * 100)
    for r in results:
        res = r["res_b"]
        if res:
            print(f"{r['name']:<25} | {res['sum_nodes']:<18,} | {int(res['sgm_nodes']):<18,} | {res['sum_times']:<10.2f}s | {res['sgm_times']:<15.3f}s")
        else:
            print(f"{r['name']:<25} | {'FAILED':<18} | {'N/A':<18} | {'N/A':<12} | {'N/A':<18}")

    # Report Set C
    print("\n### Set C: size9_300 (300 instances, single solution -s 1)")
    print(f"{'Configuration':<25} | {'Sum Nodes':<18} | {'SGM Nodes (s=1k)':<18} | {'Sum Time':<12} | {'SGM Time (s=0.1)':<18}")
    print("-" * 100)
    for r in results:
        res = r["res_c"]
        if res:
            print(f"{r['name']:<25} | {res['sum_nodes']:<18,} | {int(res['sgm_nodes']):<18,} | {res['sum_times']:<10.2f}s | {res['sgm_times']:<15.3f}s")
        else:
            print(f"{r['name']:<25} | {'FAILED':<18} | {'N/A':<18} | {'N/A':<12} | {'N/A':<18}")

    # Write report to markdown file
    with open("python_scripts/examples/validation_sweep_report.md", "w") as out:
        out.write("# Hyperparameter Validation Sweep Report\n\n")
        out.write("This report validates the top HPO sweep configurations against the original baseline solver (`main`) to check for overfitting across larger and harder sets.\n\n")
        
        out.write("## Set A: size8full (6000 instances, single solution -s 1)\n\n")
        out.write("| Configuration | Sum Nodes | SGM Nodes (s=1k) | Sum Time | SGM Time (s=0.1) |\n")
        out.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            res = r["res_a"]
            if res:
                out.write(f"| {r['name']} | {res['sum_nodes']:,} | {int(res['sgm_nodes']):,} | {res['sum_times']:.2f}s | {res['sgm_times']:.3f}s |\n")
            else:
                out.write(f"| {r['name']} | FAILED | N/A | N/A | N/A |\n")

        out.write("\n## Set B: size8_100 (100 instances, all solutions -s 0)\n\n")
        out.write("| Configuration | Sum Nodes | SGM Nodes (s=1k) | Sum Time | SGM Time (s=0.1) |\n")
        out.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            res = r["res_b"]
            if res:
                out.write(f"| {r['name']} | {res['sum_nodes']:,} | {int(res['sgm_nodes']):,} | {res['sum_times']:.2f}s | {res['sgm_times']:.3f}s |\n")
            else:
                out.write(f"| {r['name']} | FAILED | N/A | N/A | N/A |\n")

        out.write("\n## Set C: size9_300 (300 instances, single solution -s 1)\n\n")
        out.write("| Configuration | Sum Nodes | SGM Nodes (s=1k) | Sum Time | SGM Time (s=0.1) |\n")
        out.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            res = r["res_c"]
            if res:
                out.write(f"| {r['name']} | {res['sum_nodes']:,} | {int(res['sgm_nodes']):,} | {res['sum_times']:.2f}s | {res['sgm_times']:.3f}s |\n")
            else:
                out.write(f"| {r['name']} | FAILED | N/A | N/A | N/A |\n")

if __name__ == "__main__":
    main()
