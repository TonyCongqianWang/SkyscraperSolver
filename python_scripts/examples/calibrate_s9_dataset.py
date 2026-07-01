#!/usr/bin/env python3
import subprocess
import time
import concurrent.futures
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

BIN_V07 = os.path.join(ROOT_DIR, "skyscraper_solver_v07")
BIN_V08 = os.path.join(ROOT_DIR, "skyscraper_solver_v08")
BIN_MAIN = os.path.join(ROOT_DIR, "skyscraper_solver_main")

BENCHMARK_IN = os.path.join(ROOT_DIR, "puzzle_bank", "puzzle_bank9.txt")
PATH_OUT_LVL1 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_lvl1.txt")
PATH_OUT_LVL2 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_lvl2.txt")
PATH_OUT_LVL3 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_lvl3.txt")

def get_symmetries(clue_str):
    nums = list(map(int, clue_str.split()))
    n = len(nums) // 4
    T = nums[0:n]
    B = nums[n:2*n]
    L = nums[2*n:3*n]
    R = nums[3*n:4*n]
    
    # 8 symmetries in D_4
    s1 = (T, B, L, R)
    s2 = (L[::-1], R[::-1], B, T)
    s3 = (B[::-1], T[::-1], R[::-1], L[::-1])
    s4 = (R, L, T[::-1], B[::-1])
    s5 = (T[::-1], B[::-1], R, L)
    s6 = (R[::-1], L[::-1], B[::-1], T[::-1])
    s7 = (B, T, L[::-1], R[::-1])
    s8 = (L, R, T, B)
    
    symmetries = [s1, s2, s3, s4, s5, s6, s7, s8]
    sym_strings = [" ".join(map(str, s[0] + s[1] + s[2] + s[3])) for s in symmetries]
    return list(dict.fromkeys(sym_strings))

def canonize(clue_str):
    nums = list(map(int, clue_str.split()))
    n = len(nums) // 4
    T = nums[0:n]
    B = nums[n:2*n]
    L = nums[2*n:3*n]
    R = nums[3*n:4*n]
    
    s1 = (T, B, L, R)
    s2 = (L[::-1], R[::-1], B, T)
    s3 = (B[::-1], T[::-1], R[::-1], L[::-1])
    s4 = (R, L, T[::-1], B[::-1])
    s5 = (T[::-1], B[::-1], R, L)
    s6 = (R[::-1], L[::-1], B[::-1], T[::-1])
    s7 = (B, T, L[::-1], R[::-1])
    s8 = (L, R, T, B)
    
    symmetries = [s1, s2, s3, s4, s5, s6, s7, s8]
    sym_lists = [s[0] + s[1] + s[2] + s[3] for s in symmetries]
    return tuple(min(sym_lists))

def run_solver(binary, clue, timeout=120.0):
    t_start = time.perf_counter()
    try:
        proc = subprocess.Popen(
            [binary, "-s", "1", clue],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                stdout, stderr = proc.communicate(timeout=0.5)
            except Exception:
                pass
            return None
            
        elapsed = time.perf_counter() - t_start
        if proc.returncode != 0:
            return None
        return elapsed
    except Exception:
        return None

def evaluate_base_clue(clue):
    times = {}
    for name, bin_path in [("v07", BIN_V07), ("v08", BIN_V08), ("main", BIN_MAIN)]:
        t = run_solver(bin_path, clue, timeout=120.0)
        if t is None:
            return None
        times[name] = t
    return times

def evaluate_all_symmetries(clue, timeout=120.0):
    rots = get_symmetries(clue)
    tasks = []
    for rot in rots:
        for name, bin_path in [("v07", BIN_V07), ("v08", BIN_V08), ("main", BIN_MAIN)]:
            tasks.append((bin_path, rot))
            
    times = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_solver, bin_path, rot, timeout) for bin_path, rot in tasks]
        for fut in futures:
            t = fut.result()
            if t is None:
                return None
            times.append(t)
    return max(times)

def main():
    parser = argparse.ArgumentParser(description="Calibrate Size 9 Skyscraper puzzles into difficulty levels.")
    parser.add_argument("--target-lvl1", type=int, default=500, help="Target count of unique base puzzles for Level 1 (default: 500)")
    parser.add_argument("--target-lvl2", type=int, default=250, help="Target count of unique base puzzles for Level 2 (default: 250)")
    parser.add_argument("--target-lvl3", type=int, default=100, help="Target count of unique base puzzles for Level 3 (default: 100)")
    parser.add_argument("--scan-start", type=int, default=0, help="Start index of puzzle bank scan (default: 0)")
    parser.add_argument("--scan-end", type=int, default=10000, help="End index of puzzle bank scan (default: 10000)")
    parser.add_argument("--max-workers", type=int, default=8, help="Number of concurrent worker threads (default: 8)")
    args = parser.parse_args()

    for path in [BIN_V07, BIN_V08, BIN_MAIN]:
        if not os.path.exists(path):
            print(f"Error: Binary {path} not found. Please compile it first.")
            sys.exit(1)
            
    print(f"Loading candidate puzzles from {BENCHMARK_IN}...")
    with open(BENCHMARK_IN, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    print(f"Loaded {len(lines)} raw puzzles.")
    
    candidates = {}
    count_timed_out = 0
    count_trivial_discarded = 0
    
    # Phase 1: Filter base clues (under 120s)
    print("Phase 1: Broad Base-Clue Filtering...")
    
    scan_start = args.scan_start
    scan_end = min(args.scan_end, len(lines))
    chunk = lines[scan_start:scan_end]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(evaluate_base_clue, clue): clue for clue in chunk}
        
        for i, fut in enumerate(concurrent.futures.as_completed(futures)):
            clue = futures[fut]
            times = fut.result()
            
            if times is not None:
                key = canonize(clue)
                if key not in candidates:
                    candidates[key] = clue
            else:
                count_timed_out += 1
                        
            if (i + 1) % 500 == 0:
                print(f"  Processed {i+1}/{len(chunk)} base clues... Candidates: {len(candidates)}")
                
    print(f"Base Clue Filtering complete. Found {len(candidates)} unique candidates.")
    
    # Phase 2: Symmetry Verification and Classification
    print("\nPhase 2: Symmetry Verification & Classification (120s timeout)...")
    
    verified_lvl1 = []
    verified_lvl2 = []
    verified_lvl3 = []
    
    candidate_keys = list(candidates.keys())
    for count, key in enumerate(candidate_keys):
        clue = candidates[key]
        t_max = evaluate_all_symmetries(clue, timeout=120.0)
        
        if t_max is not None:
            if t_max < 0.1:
                count_trivial_discarded += 1
            elif 0.1 <= t_max < 2.0:
                verified_lvl1.append(clue)
                print(f"  [LVL 1] {len(verified_lvl1)} Verified: t_max = {t_max:.2f}s (Base: {clue[:20]}...)")
            elif 2.0 <= t_max < 25.0:
                verified_lvl2.append(clue)
                print(f"  [LVL 2] {len(verified_lvl2)} Verified: t_max = {t_max:.2f}s (Base: {clue[:20]}...)")
            elif t_max >= 25.0:
                verified_lvl3.append(clue)
                print(f"  [LVL 3] {len(verified_lvl3)} Verified: t_max = {t_max:.2f}s (Base: {clue[:20]}...)")
        else:
            count_timed_out += 1
                    
        # Early stop if we have enough of all levels
        if len(verified_lvl1) >= args.target_lvl1 and len(verified_lvl2) >= args.target_lvl2 and len(verified_lvl3) >= args.target_lvl3:
            print("Successfully verified target counts for all three levels!")
            break
            
        if (count + 1) % 50 == 0:
            print(f"  Checked {count+1}/{len(candidate_keys)} candidates... (Lvl 1: {len(verified_lvl1)}, Lvl 2: {len(verified_lvl2)}, Lvl 3: {len(verified_lvl3)}, Trivial Discarded: {count_trivial_discarded})")
            
    print(f"\nVerification complete. Lvl 1 verified: {len(verified_lvl1)}, Lvl 2 verified: {len(verified_lvl2)}, Lvl 3 verified: {len(verified_lvl3)}")
    print(f"Total timed out (too difficult): {count_timed_out}")
    print(f"Total discarded as trivial: {count_trivial_discarded}")
    
    if len(verified_lvl1) < args.target_lvl1:
        print(f"Warning: Only verified {len(verified_lvl1)} Lvl 1 puzzles (target {args.target_lvl1}).")
    if len(verified_lvl2) < args.target_lvl2:
        print(f"Warning: Only verified {len(verified_lvl2)} Lvl 2 puzzles (target {args.target_lvl2}).")
    if len(verified_lvl3) < args.target_lvl3:
        print(f"Warning: Only verified {len(verified_lvl3)} Lvl 3 puzzles (target {args.target_lvl3}).")
        
    # Expand and save Lvl 1 puzzles
    lvl1_expanded = []
    for clue in verified_lvl1:
        lvl1_expanded.extend(get_symmetries(clue))
    lvl1_expanded = list(dict.fromkeys(lvl1_expanded))
    
    os.makedirs(os.path.dirname(PATH_OUT_LVL1), exist_ok=True)
    with open(PATH_OUT_LVL1, "w") as f:
        for clue in lvl1_expanded:
            f.write(f'"{clue}"\n')
    print(f"Wrote {len(lvl1_expanded)} Lvl 1 symmetric variants ({len(verified_lvl1)} unique base puzzles) to {PATH_OUT_LVL1}")
    
    # Expand and save Lvl 2 puzzles
    lvl2_expanded = []
    for clue in verified_lvl2:
        lvl2_expanded.extend(get_symmetries(clue))
    lvl2_expanded = list(dict.fromkeys(lvl2_expanded))
    
    os.makedirs(os.path.dirname(PATH_OUT_LVL2), exist_ok=True)
    with open(PATH_OUT_LVL2, "w") as f:
        for clue in lvl2_expanded:
            f.write(f'"{clue}"\n')
    print(f"Wrote {len(lvl2_expanded)} Lvl 2 symmetric variants ({len(verified_lvl2)} unique base puzzles) to {PATH_OUT_LVL2}")
    
    # Expand and save Lvl 3 puzzles
    lvl3_expanded = []
    for clue in verified_lvl3:
        lvl3_expanded.extend(get_symmetries(clue))
    lvl3_expanded = list(dict.fromkeys(lvl3_expanded))
    
    os.makedirs(os.path.dirname(PATH_OUT_LVL3), exist_ok=True)
    with open(PATH_OUT_LVL3, "w") as f:
        for clue in lvl3_expanded:
            f.write(f'"{clue}"\n')
    print(f"Wrote {len(lvl3_expanded)} Lvl 3 symmetric variants ({len(verified_lvl3)} unique base puzzles) to {PATH_OUT_LVL3}")
    
    print("\nSize 9 Dataset Calibration Completed Successfully!")

if __name__ == "__main__":
    main()
