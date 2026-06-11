#!/usr/bin/env python3
"""
Multi-phase HPO gauntlet for skyscraper solver selection-strategy tuning.

Pipeline
--------
  0. Compile all parameter combinations (sequential, to avoid obj/ races).
  1. Deduplicate: fingerprint each binary on a calibration instance and drop
     behaviorally-equivalent configs.  Any config with SEL+EXTRA << 100 always
     rebuilds every step (progress increments by +100 per set_grid_val), making
     the LIN/QUAD/SEL values irrelevant – those collapse to one equivalence class.
  2. Phase 1 – node filter on small benchmarks, many workers (no timing noise).
     Drops the worst fraction by total nodes visited.
  3. Phase 2 – timing filter on the same small benchmarks, 4 workers.
     Drops the slowest fraction of surviving configs.
  4. Phase 3 – timing filter on medium benchmarks, 4 workers (more signal).
     Drops the slowest fraction of surviving configs.
  5. Phase 4 – final timing on full benchmark sets, 4 workers.  Reports all
     survivors ranked by time and by nodes.
"""
import subprocess
import os
import shutil
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

# Single instance used to fingerprint binary behaviour for deduplication
CALIB_INSTANCE = "2 3 3 2 1 3 3 3 2 4 3 3 1 3 4 1 2 4 2 2 3 2 3 2 1 3 3 2"

# ── gauntlet definition ───────────────────────────────────────────────────────
# Each entry: (label, s7_file, s8_file, metric, keep_top_fraction, workers)
#   metric          – "nodes" or "time"
#   keep_top_fraction – fraction of survivors to keep (None = keep all, report only)
GAUNTLET = [
    # Phase 1: cheap node-count filter – weed out obviously bad configs quickly
    ("Phase 1 – node filter  (tiny sets)",
     S7_TINY,  S8_TINY,   "nodes", 0.50, WORKERS_NODES),
    # Phase 2: first timing filter on the same small sets
    ("Phase 2 – time filter  (small sets)",
     S7_SMALL, S8_TINY,   "time",  0.50, WORKERS_TIME),
    # Phase 3: timing on medium sets for better statistical signal
    ("Phase 3 – time filter  (medium sets)",
     S7_SMALL, S8_MEDIUM, "time",  0.50, WORKERS_TIME),
    # Phase 4: final timing on full sets – all survivors are reported
    ("Phase 4 – final timing (full sets)",
     S7_FULL,  S8_MEDIUM, "time",  None, WORKERS_TIME),
]


# ── helpers ───────────────────────────────────────────────────────────────────
def load_instances(filepath):
    with open(filepath) as f:
        return [l.strip().strip('"') for l in f if l.strip()]


def binary_path(idx):
    return f"obj/hpo_{idx}"


# ── compile / calibrate ───────────────────────────────────────────────────────
def compile_config(idx, sel, extra, thresh, lin, quad):
    """Compile one configuration into obj/hpo_{idx}.  Sequential callers only."""
    # Force recompile of the one file that holds the tunable macros.
    for stale in ("obj/sel_strat_routing.o", "skyscraper_solver"):
        if os.path.exists(stale):
            os.remove(stale)

    cflags = (
        f"-Wall -Wextra -Werror -O2 "
        f"-DG_SEL_REBUILD_PERIOD={sel} "
        f"-DG_SEL_EXTRA_PERIOD_DEEP={extra} "
        f"-DG_SEL_DEPTH_THRESHOLD_0={thresh} "
        f"-DG_SEL_LINEAR_COEFF={lin} "
        f"-DG_SEL_QUAD_COEFF={quad}"
    )
    r = subprocess.run(f"make CFLAGS='{cflags}'", shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode != 0:
        return False
    shutil.copy("skyscraper_solver", binary_path(idx))
    return True


def get_calib_nodes(idx):
    """Return node count on the calibration instance, or None on failure."""
    try:
        r = subprocess.run(
            [binary_path(idx), "-s", "0", CALIB_INSTANCE],
            capture_output=True, text=True, timeout=5.0)
        for line in r.stdout.splitlines():
            if line.startswith("Nodes visited:"):
                return int(line.split(":")[1].strip())
    except Exception:
        pass
    return None


# ── single-instance solver call ───────────────────────────────────────────────
def run_solver(bin_path, option_str, clue):
    try:
        r = subprocess.run(
            [bin_path] + option_str.split() + [clue],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=2.0)
        if r.returncode != 0:
            return None
        for line in r.stdout.splitlines():
            if line.startswith("Nodes visited:"):
                return int(line.split(":")[1].strip())
    except Exception:
        pass
    return None


# ── config evaluator (runs in a worker thread) ────────────────────────────────
def evaluate_config(conf, s7_instances, s8_instances):
    """Return updated conf dict with 'nodes' and 'time', or None on failure."""
    bin_path = binary_path(conf["idx"])
    t_start  = time.time()
    total_nodes = 0

    for instances, opt in [(s7_instances, "-s 0"), (s8_instances, "-s 1")]:
        for clue in instances:
            n = run_solver(bin_path, opt, clue)
            if n is None:
                return None
            total_nodes += n

    return {**conf, "nodes": total_nodes, "time": time.time() - t_start}


# ── one gauntlet phase ────────────────────────────────────────────────────────
def run_phase(label, configs, s7_file, s8_file, metric, keep_frac, workers):
    s7 = load_instances(s7_file)
    s8 = load_instances(s8_file)
    n_total = len(configs)

    print(f"\n{'='*72}")
    print(f"  {label}")
    print(f"  {n_total} configs | S7={len(s7)} | S8={len(s8)} | "
          f"metric={metric} | keep={'all' if keep_frac is None else f'{keep_frac:.0%}'} "
          f"| workers={workers}")
    print(f"{'='*72}")
    sys.stdout.flush()

    results  = []
    lock     = threading.Lock()
    done_ref = [0]
    report_every = max(1, n_total // 10)

    def task(conf):
        res = evaluate_config(conf, s7, s8)
        with lock:
            done_ref[0] += 1
            n = done_ref[0]
            if n % report_every == 0 or n == n_total:
                c = conf["params"]
                elapsed = res["time"] if res else -1
                status = "FAILED" if res is None else f"nodes={res['nodes']:,}  t={elapsed:.2f}s"
                print(f"  [{n}/{n_total}] idx={conf['idx']:4d} "
                      f"(SEL={c[0]},EXTRA={c[1]},TH0={c[2]},"
                      f"LIN={c[3]},QUAD={c[4]}) {status}")
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

    results.sort(key=lambda r: r[metric])

    if keep_frac is not None:
        n_keep   = max(5, int(len(results) * keep_frac))
        n_drop   = len(results) - n_keep
        results  = results[:n_keep]
        print(f"  Kept {len(results)}, dropped {n_drop} worst by {metric}.")
    else:
        print(f"  Final phase – all {len(results)} survivors.")

    print(f"\n  Top 10 by {metric}:")
    for i, r in enumerate(results[:10]):
        c = r["params"]
        print(f"    {i+1:2d}. idx={r['idx']:4d} "
              f"(SEL={c[0]},EXTRA={c[1]},TH0={c[2]},LIN={c[3]},QUAD={c[4]}) "
              f"nodes={r['nodes']:,}  time={r['time']:.3f}s")
    sys.stdout.flush()
    return results


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    # ── parameter grid ─────────────────────────────────────────────────────────
    # Progress increments by +100 per set_grid_val call.
    # Effective period at depth > thresh_0  =  SEL + EXTRA + poly(x).
    # Interesting regime: period crosses the 100-mark during search.
    # SEL alone governs shallow depth; SEL+EXTRA governs deep depth.
    #
    # Very low values (SEL+EXTRA << 100) → always rebuild → all equivalent.
    # Very high values (SEL+EXTRA >> 100) → never rebuild → no benefit.
    # The sweet spot is where the polynomial can push period across 100.

    sel_periods   = [4, 16, 32, 64, 128, 256]       # shallow-depth base period
    extra_periods = [32, 64, 128, 256]               # extra period added at depth > thresh
    thresholds    = [0, 1, 2]                        # depth at which EXTRA activates
    linear_coeffs = [0.0, 4.0, 16.0, 64.0, 256.0]  # linear term coefficient
    quad_coeffs   = [0.0, 0.5, 2.0, 8.0]            # quadratic term coefficient

    all_params = [
        (idx, sel, extra, thresh, lin, quad)
        for idx,  (sel, extra, thresh, lin, quad) in enumerate(
            (sel, extra, thresh, lin, quad)
            for sel   in sel_periods
            for extra in extra_periods
            for thresh in thresholds
            for lin   in linear_coeffs
            for quad  in quad_coeffs
        )
    ]
    total = len(all_params)
    print(f"Generated {total} parameter combinations.")
    print(f"Grid: SEL×{len(sel_periods)} EXTRA×{len(extra_periods)} "
          f"TH0×{len(thresholds)} LIN×{len(linear_coeffs)} QUAD×{len(quad_coeffs)}")

    # ── compile ────────────────────────────────────────────────────────────────
    os.makedirs("obj", exist_ok=True)
    print(f"\nCompiling {total} configurations (sequential)…")
    t0 = time.time()
    compiled = []
    for i, (idx, sel, extra, thresh, lin, quad) in enumerate(all_params):
        ok = compile_config(idx, sel, extra, thresh, lin, quad)
        if ok:
            compiled.append({"idx": idx,
                             "params": (sel, extra, thresh, lin, quad)})
        if (i + 1) % 100 == 0 or (i + 1) == total:
            rate = (i + 1) / (time.time() - t0)
            eta  = (total - i - 1) / rate
            print(f"  Compiled {i+1}/{total} "
                  f"({time.time()-t0:.0f}s elapsed, ETA {eta:.0f}s)…")
            sys.stdout.flush()
    print(f"Compiled {len(compiled)}/{total} configs in {time.time()-t0:.1f}s")

    # ── deduplicate ────────────────────────────────────────────────────────────
    print("\nDeduplicating via calibration instance…")
    sys.stdout.flush()
    seen: dict[int, int] = {}   # calib_nodes -> first idx
    unique = []
    n_dup  = 0
    for conf in compiled:
        n = get_calib_nodes(conf["idx"])
        if n is None:
            print(f"  WARNING: calibration failed for idx={conf['idx']}, skipping.")
            continue
        if n in seen:
            n_dup += 1
            p = binary_path(conf["idx"])
            if os.path.exists(p):
                os.remove(p)
        else:
            seen[n] = conf["idx"]
            unique.append(conf)
    print(f"  {len(unique)} unique configs ({n_dup} duplicates removed).")
    sys.stdout.flush()

    # ── gauntlet ───────────────────────────────────────────────────────────────
    survivors = unique
    for label, s7_file, s8_file, metric, keep_frac, workers in GAUNTLET:
        survivors = run_phase(label, survivors, s7_file, s8_file,
                              metric, keep_frac, workers)
        if not survivors:
            print("No survivors – aborting gauntlet.")
            break

    # ── final report ───────────────────────────────────────────────────────────
    if survivors:
        print(f"\n{'='*72}")
        print("FINAL RANKING")
        print(f"{'='*72}")
        print("\nTop 15 by time:")
        for i, r in enumerate(sorted(survivors, key=lambda x: x["time"])[:15]):
            c = r["params"]
            print(f"  {i+1:2d}. (SEL={c[0]},EXTRA={c[1]},TH0={c[2]},"
                  f"LIN={c[3]},QUAD={c[4]}) "
                  f"time={r['time']:.3f}s  nodes={r['nodes']:,}")
        print("\nTop 15 by nodes:")
        for i, r in enumerate(sorted(survivors, key=lambda x: x["nodes"])[:15]):
            c = r["params"]
            print(f"  {i+1:2d}. (SEL={c[0]},EXTRA={c[1]},TH0={c[2]},"
                  f"LIN={c[3]},QUAD={c[4]}) "
                  f"nodes={r['nodes']:,}  time={r['time']:.3f}s")

    # ── cleanup ────────────────────────────────────────────────────────────────
    print("\nCleaning up binaries…")
    for conf in compiled:
        p = binary_path(conf["idx"])
        if os.path.exists(p):
            os.remove(p)
    print("Done.")


if __name__ == "__main__":
    main()
