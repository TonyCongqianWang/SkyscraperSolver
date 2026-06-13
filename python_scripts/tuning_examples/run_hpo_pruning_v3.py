#!/usr/bin/env python3
"""
================================================================================
HPO PRUNING TUNING GAUNTLET V4 (NEIGHBORHOOD SWEEP & STRATIFIED DEDUPLICATION)
================================================================================

CONCEPT & METHODOLOGY FOR THE NEXT AGENT:
-----------------------------------------
1. Neighborhood Definition:
   This gauntlet is configured to run a highly focused neighborhood sweep around
   the top performing configurations from HPO V3 and V4 (balancing nodes vs times):
   - Time Winner (idx=5045):   (MIN_U=0.50, SHAL=200, DEEP=100, TH=(1,4), GAC=0.55, Curve 11)
   - Node Winner (idx=9840):   (MIN_U=0.56, SHAL=200, DEEP=100, TH=(1,4), GAC=0.55, Curve 2)
   - Selected Default (idx=9172): (MIN_U=0.53, SHAL=360, DEEP=50,  TH=(1,4), GAC=0.55, Curve 10)
   
   The grid generates 29,160 configs around these values.

2. Stratified Filtering and Calibration Deduplication (Crucial Change):
   - Phase 1 (cheap node filter on 100 S7 + 50 S8 instances) is executed first on
     all 29,160 configurations. Since Phase 1 is extremely fast (only checks node counts),
     it behaves as a high-throughput pre-filter.
   - Stratified Filtering: The Phase 1 results are grouped by their GAC threshold
     parameters and filtered to keep only the top 20% by node count in each GAC group.
     This ensures GAC parameter diversity is not prematurely lost.
   - Post-Phase 1 Deduplication: Calibration deduplication (using 5 representative
     instances: 1 size-7, 1 size-8, and 3 hard size-9 instances) is run *after* Phase 1
     on the surviving configurations. Because size-9 instances are computationally
     intensive, running them only on Phase 1 survivors avoids massive CPU overhead.
   - High Timeout Safeguard: A high timeout (10.0 seconds) is used during calibration
     to prevent temporary CPU spikes or variance in single-solution runs from falsely
     discarding excellent configurations.
   - Skip to Phase 2: If the population of unique configurations after calibration
     drops below 2000, we skip Phase 1b (tiny sets time filter) entirely and route them
     directly to Phase 2 (small sets time filter) to optimize execution time.

HOW TO RUN:
-----------
1. Build the solver binary and ensure verify_consistency.py passes:
   $ make clean && make
   $ python3 python_scripts/verify_consistency.py
   
2. Run the HPO script (do NOT run it now, as requested by the user):
   $ python3 python_scripts/examples/run_hpo_pruning_v3.py 2>&1 | tee python_scripts/examples/hpo_pruning_results_v4.log
   
3. Once complete, inspect the log for the winners, apply the new parameter macros
   to src/prune_strat_routing.c, and run verify_consistency.py to ensure correctness.
"""
import subprocess
import os
import concurrent.futures
import threading
import time
import sys

# ── tuneable constants ────────────────────────────────────────────────────────
WORKERS_NODES = 12   # node-count phases: many workers, no timing noise concern
WORKERS_TIME  = 4    # timing phases: fewer workers to reduce contention noise

# Benchmark files used across phases (relative to project root)
S7_TINY   = "benchmark_sets/benchmarkSet7_subset100.txt"   # 100  instances
S7_SMALL  = "benchmark_sets/benchmarkSet7_easy500.txt"     # 500  instances
S7_FULL   = "benchmark_sets/benchmarkSet7.txt"             # 6000 instances
S8_TINY   = "benchmark_sets/benchmarkSet8_easy50.txt"      # 50   instances
S8_MEDIUM = "benchmark_sets/benchmarkSet8_subset300.txt"   # 300  instances

# Predefined curves (a, b, c)
curves = [
    (0.0, 0.0, 0.0), # Curve 0
    (0.5, 0.2, 0.0), # Curve 1
    (1.0, 0.5, 0.1), # Curve 2 (in sweep)
    (2.0, 1.0, 0.3), # Curve 3 (in sweep)
    (3.0, 2.0, 1.0), # Curve 4
    (0.1, 1.5, 0.0), # Curve 5 (in sweep)
    (0.0, 0.2, 2.0), # Curve 6
    (0.2, 1.0, 1.5), # Curve 7 (in sweep)
    (0.5, 0.5, 0.1), # Curve 8
    (1.5, 0.8, 0.2), # Curve 9
    (0.2, 0.5, 1.0), # Curve 10
    (0.5, 1.0, 0.5)  # Curve 11
]

# ── gauntlet definition ───────────────────────────────────────────────────────
GAUNTLET = [
    # Phase 1b: first timing filter on tiny sets
    ("Phase 1b – tiny sets time filter",
     S7_TINY,  S8_TINY,   "time",  0.50, WORKERS_TIME),
    # Phase 2: second timing filter on small sets
    ("Phase 2 – time filter  (small sets)",
     S7_SMALL, S8_TINY,   "time",  0.30, WORKERS_TIME),
    # Phase 3: timing on medium sets for better statistical signal
    ("Phase 3 – time filter  (medium sets)",
     S7_SMALL, S8_MEDIUM, "time",  0.15, WORKERS_TIME),
    # Phase 4: final timing on full sets – all survivors are reported
    ("Phase 4 – final timing (full sets)",
     S7_FULL,  S8_MEDIUM, "time",  None, WORKERS_TIME),
]

# ── helpers ───────────────────────────────────────────────────────────────────
def load_instances(filepath):
    with open(filepath) as f:
        return [l.strip().strip('"') for l in f if l.strip()]

def get_env_for_params(params):
    min_u, shal, deep, th0, th1, gac, c_idx, kp = params
    lin, quad, cubic = curves[c_idx]

    env = os.environ.copy()
    env["G_MIN_UNSET_R_PRUNE"] = str(min_u)
    env["G_PRUNE_PERIOD_SHALLOW"] = str(shal)
    env["G_PRUNE_EXTRA_PERIOD_DEEP"] = str(deep)
    env["G_PRUNE_DEPTH_THRESHOLD_0"] = str(th0)
    env["G_PRUNE_DEPTH_THRESHOLD_1"] = str(th1)
    env["G_PRUNE_GAC_UNSET_R_THRESHOLD"] = str(gac)
    env["G_PRUNE_LIN_COEFF"] = str(lin)
    env["G_PRUNE_QUAD_COEFF"] = str(quad)
    env["G_PRUNE_CUBIC_COEFF"] = str(cubic)
    env["KEEP_PRUNING"] = str(kp)
    return env

# ── single-instance solver call ───────────────────────────────────────────────
def run_solver(env, option_str, clue, timeout=2.0):
    try:
        r = subprocess.run(
            ["./skyscraper_solver"] + option_str.split() + [clue],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=timeout, env=env)
        if r.returncode != 0:
            return None
        for line in r.stdout.splitlines():
            if line.startswith("Nodes visited:"):
                return int(line.split(":")[1].strip())
    except Exception:
        pass
    return None

# ── config evaluator (runs in a worker thread) ────────────────────────────────
def evaluate_config(conf, s7_instances, s8_instances, max_nodes_cutoff=None):
    """Return updated conf dict with 'nodes' and 'time', or None on failure."""
    env = get_env_for_params(conf["params"])
    t_start  = time.time()
    total_nodes = 0

    for instances, opt in [(s7_instances, "-s 0"), (s8_instances, "-s 0")]:
        for clue in instances:
            n = run_solver(env, opt, clue)
            if n is None:
                return None
            total_nodes += n
            if max_nodes_cutoff is not None and total_nodes > max_nodes_cutoff:
                return None

    return {**conf, "nodes": total_nodes, "time": time.time() - t_start}

# ── one gauntlet phase ────────────────────────────────────────────────────────
def run_phase(label, configs, s7_file, s8_file, metric, keep_frac, workers):
    s7 = load_instances(s7_file)
    s8 = load_instances(s8_file)
    n_total = len(configs)

    print(f"\n{'='*72}")
    print(f"  {label}")
    print(f"  {n_total} configs | S7={len(s7)} | S8={len(s8)} | "
          f"metric={metric} | keep={f'{keep_frac:.0%}' if keep_frac is not None else 'all'} "
          f"| workers={workers}")
    print(f"{'='*72}")
    sys.stdout.flush()

    results  = []
    lock     = threading.Lock()
    done_ref = [0]
    report_every = max(1, n_total // 10)

    def task(conf):
        cutoff = 850000 if label.startswith("Phase 1 – node filter") else None
        res = evaluate_config(conf, s7, s8, cutoff)
        with lock:
            done_ref[0] += 1
            n = done_ref[0]
            if n % report_every == 0 or n == n_total:
                c = conf["params"]
                elapsed = res["time"] if res else -1
                status = "FAILED/PRUNED" if res is None else f"nodes={res['nodes']:,}  t={elapsed:.2f}s"
                print(f"  [{n}/{n_total}] idx={conf['idx']:4d} "
                      f"(MIN_U={c[0]},SHAL={c[1]},DEEP={c[2]},TH=({c[3]},{c[4]}),"
                      f"GAC={c[5]},C={c[6]},KP={c[7]}) {status}")
                sys.stdout.flush()
        return res

    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(task, configs):
            if res:
                results.append(res)

    print(f"\n  Evaluated {len(results)}/{n_total} configs in {time.time()-t0:.1f}s")

    if not results:
        return []

    # Sort results by metric
    results.sort(key=lambda r: r[metric])

    if label.startswith("Phase 1 – node filter"):
        from collections import defaultdict
        gac_groups = defaultdict(list)
        for r in results:
            gac_val = r["params"][5]
            gac_groups[gac_val].append(r)
        
        survivors = []
        for gac_val, grp in gac_groups.items():
            grp.sort(key=lambda x: x["nodes"])
            n_keep = max(5, int(len(grp) * keep_frac))
            survivors.extend(grp[:n_keep])
            print(f"  GAC threshold {gac_val}: kept {n_keep} / {len(grp)} configs.")
        
        # Sort survivors by nodes
        survivors.sort(key=lambda r: r[metric])
        print(f"  Total kept: {len(survivors)}, dropped {len(results) - len(survivors)} worst.")
        results = survivors
    elif keep_frac is not None:
        n_keep = max(5, int(len(results) * keep_frac))
        if "Phase 1b" in label:
            n_keep = max(n_keep, min(2000, len(results)))
        n_drop   = len(results) - n_keep
        results  = results[:n_keep]
        print(f"  Kept {len(results)}, dropped {n_drop} worst by {metric}.")
    else:
        print(f"  Final phase – all {len(results)} survivors.")

    print(f"\n  Top 10 by {metric}:")
    for i, r in enumerate(results[:10]):
        c = r["params"]
        print(f"    {i+1:2d}. idx={r['idx']:4d} "
              f"(MIN_U={c[0]},SHAL={c[1]},DEEP={c[2]},TH=({c[3]},{c[4]}),GAC={c[5]},C={c[6]},KP={c[7]}) "
              f"nodes={r['nodes']:,}  time={r['time']:.3f}s")
    sys.stdout.flush()
    return results

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    # Pre-compile the solver once with env support enabled
    print("Building solver binary with env support...")
    subprocess.run("make clean && make CFLAGS=\"-Wall -Wextra -Werror -O2 -DG_PRUNE_NO_ENV=0\"", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Parameter grid definition (focused neighborhood around V4 winners: 5045, 9840, 9172)
    min_unsets = [0.48, 0.50, 0.52, 0.54, 0.56, 0.58]
    period_shallows = [180, 200, 220, 340, 360, 380]
    extra_deeps = [40, 50, 60, 80, 100, 120]
    depth_thresholds = [(1, 3), (1, 4), (1, 5)]
    gac_unsets = [0.50, 0.53, 0.55, 0.57, 0.60]
    curves_indices = [2, 10, 11]
    keep_prunings = [0]

    # Generate grid
    configs = []
    idx = 0
    for min_u in min_unsets:
        for shal in period_shallows:
            for deep in extra_deeps:
                for th0, th1 in depth_thresholds:
                    for gac in gac_unsets:
                        for c_idx in curves_indices:
                            for kp in keep_prunings:
                                configs.append({
                                    "idx": idx,
                                    "params": (min_u, shal, deep, th0, th1, gac, c_idx, kp)
                                })
                                idx += 1

    total = len(configs)
    print(f"Generated {total} parameter combinations.")
    sys.stdout.flush()

    # ── Phase 1: Cheap node filter on all configs ─────────────────────────────
    # This filters down configurations to the top 20% per GAC threshold based on search nodes
    survivors = run_phase("Phase 1 – node filter  (tiny sets)", configs, S7_TINY, S8_TINY, "nodes", 0.20, WORKERS_NODES)

    # ── Deduplicate via Calibration ──────────────────────────────────────────
    # Run calibration ONLY on the Phase 1 survivors to save significant time, using a higher 10.0s timeout
    s7_all = load_instances(S7_TINY)
    s8_all = load_instances(S8_TINY)
    s9_all = load_instances("benchmark_sets/benchmarkSet9_small.txt")
    calib_s7 = s7_all[:1]
    calib_s8 = s8_all[:1]
    calib_s9 = s9_all[:3]

    print(f"\nDeduplicating via 5 calibration instances (1 size-7, 1 size-8, 3 size-9) with 10.0s timeout ({WORKERS_NODES} workers)…")
    sys.stdout.flush()

    from collections import defaultdict
    fingerprint_groups = defaultdict(list)
    fingerprint_lock = threading.Lock()
    n_fail = 0

    def get_calib_fingerprint(params, timeout=10.0):
        env = get_env_for_params(params)
        total_nodes = 0
        for clue in calib_s7:
            n = run_solver(env, "-s 0", clue, timeout=timeout)
            if n is None:
                return None
            total_nodes += n
        for clue in calib_s8:
            n = run_solver(env, "-s 0", clue, timeout=timeout)
            if n is None:
                return None
            total_nodes += n
        for clue in calib_s9:
            n = run_solver(env, "-s 1", clue, timeout=timeout)
            if n is None:
                return None
            total_nodes += n
        return total_nodes

    def calib_task(conf):
        nonlocal n_fail
        f = get_calib_fingerprint(conf["params"], timeout=10.0)
        if f is None:
            with fingerprint_lock:
                n_fail += 1
            return None
        with fingerprint_lock:
            fingerprint_groups[f].append(conf)
        return conf

    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS_NODES) as ex:
        list(ex.map(calib_task, survivors))

    # Ensure baseline is chosen as representative if present
    baseline_params = (0.50, 240, 100, 1, 4, 0.60, 2, 0)
    for f in fingerprint_groups:
        grp = fingerprint_groups[f]
        for i, c in enumerate(grp):
            if c["params"] == baseline_params:
                grp[0], grp[i] = grp[i], grp[0]
                break

    unique_configs = []
    n_dup = 0
    sorted_fingerprints = sorted(fingerprint_groups.keys())
    for f in sorted_fingerprints:
        grp = fingerprint_groups[f]
        unique_configs.append(grp[0])
        n_dup += len(grp) - 1

    print(f"  {len(unique_configs)} unique configs ({n_dup} duplicates removed, {n_fail} failed) in {time.time()-t0:.1f}s.")
    sys.stdout.flush()

    # Perform qualitative duplicate analysis and write to log
    print("Writing duplicates analysis to python_scripts/examples/hpo_duplicates_analysis.log...")
    p_names = ["MIN_U", "SHAL", "DEEP", "TH0", "TH1", "GAC", "C_IDX", "KP"]
    var_counts = defaultdict(int)
    
    with open("python_scripts/examples/hpo_duplicates_analysis.log", "w") as out_log:
        out_log.write("HPO DUPLICATE CONFIGURATIONS QUALITATIVE ANALYSIS\n")
        out_log.write("==================================================\n\n")
        out_log.write(f"Total configurations input to calibration: {len(survivors)}\n")
        out_log.write(f"Unique configurations kept:              {len(unique_configs)}\n")
        out_log.write(f"Duplicate configurations:                 {n_dup}\n\n")
        
        out_log.write("Analysis of Parameter Variations within identical behavior groups:\n")
        out_log.write("-------------------------------------------------------------------\n")
        
        large_groups = sorted(fingerprint_groups.items(), key=lambda x: len(x[1]), reverse=True)
        for rank, (f, grp) in enumerate(large_groups[:20], 1):
            out_log.write(f"\nGroup {rank}: Fingerprint = {f} nodes | Size = {len(grp)} configs\n")
            varying = []
            constant = {}
            for col_idx, p_name in enumerate(p_names):
                vals = set(c["params"][col_idx] for c in grp)
                if len(vals) == 1:
                    constant[p_name] = list(vals)[0]
                else:
                    varying.append((p_name, sorted(list(vals))))
                    var_counts[p_name] += 1
            out_log.write("  Constants: " + ", ".join(f"{k}={v}" for k, v in constant.items()) + "\n")
            out_log.write("  Varying:   " + ", ".join(f"{k} in {v}" for k, v in varying) + "\n")
            
        out_log.write("\nSummary of Redundant/Inactive Parameters in Calibration:\n")
        out_log.write("--------------------------------------------------------\n")
        for p_name in p_names:
            cnt = var_counts[p_name]
            out_log.write(f"  Parameter '{p_name}' varies in {cnt} duplicate groups.\n")
            
    print("  Analysis summary: Parameter variations in duplicate groups:")
    for p_name in p_names:
        print(f"    - {p_name}: varies in {var_counts[p_name]} duplicate groups.")
    sys.stdout.flush()

    # ── gauntlet ───────────────────────────────────────────────────────────────
    survivors = unique_configs
    for label, s7_file, s8_file, metric, keep_frac, workers in GAUNTLET:
        if (label.startswith("Phase 1b") or label.startswith("Phase 2")) and len(survivors) <= 2000:
            print(f"\n  Skipping {label.split('–')[0].strip()} (population is already at or below 2000: {len(survivors)} configs).")
            continue
        survivors = run_phase(label, survivors, s7_file, s8_file,
                               metric, keep_frac, workers)
        if not survivors:
            print("No survivors – aborting gauntlet.")
            break

    # ── final report ───────────────────────────────────────────────────────────
    if survivors:
        # Find baseline survivor and stats
        baseline_params = (0.50, 240, 100, 1, 4, 0.60, 2, 0)
        baseline_survivor = None
        for r in survivors:
            if r["params"] == baseline_params:
                baseline_survivor = r
                break

        print(f"\n{'='*72}")
        print("FINAL RANKING")
        print(f"{'='*72}")

        if baseline_survivor:
            b_time = baseline_survivor["time"]
            b_nodes = baseline_survivor["nodes"]
            print(f"\nBaseline Config Stats: time={b_time:.3f}s  nodes={b_nodes:,}")
        else:
            print("\nBaseline Config Stats: Baseline did not survive to the final phase.")

        print("\nTop 15 by time:")
        for i, r in enumerate(sorted(survivors, key=lambda x: x["time"])[:15]):
            c = r["params"]
            rel_t = ""
            if baseline_survivor:
                diff_t = (r["time"] - b_time) / b_time * 100
                rel_t = f" ({diff_t:+.2f}%)"
            print(f"  {i+1:2d}. idx={r['idx']:4d} "
                  f"(MIN_U={c[0]},SHAL={c[1]},DEEP={c[2]},TH=({c[3]},{c[4]}),"
                  f"GAC={c[5]},C={c[6]},KP={c[7]}) "
                  f"time={r['time']:.3f}s{rel_t}  nodes={r['nodes']:,}")

        print("\nTop 15 by nodes:")
        for i, r in enumerate(sorted(survivors, key=lambda x: x["nodes"])[:15]):
            c = r["params"]
            rel_n = ""
            if baseline_survivor:
                diff_n = (r["nodes"] - b_nodes) / b_nodes * 100
                rel_n = f" ({diff_n:+.2f}%)"
            print(f"  {i+1:2d}. idx={r['idx']:4d} "
                  f"(MIN_U={c[0]},SHAL={c[1]},DEEP={c[2]},TH=({c[3]},{c[4]}),"
                  f"GAC={c[5]},C={c[6]},KP={c[7]}) "
                  f"nodes={r['nodes']:,}{rel_n}  time={r['time']:.3f}s")

if __name__ == "__main__":
    main()
