#!/usr/bin/env python3
import subprocess
import time
import concurrent.futures
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

BIN_DEV = os.path.join(ROOT_DIR, "skyscraper_solver_dev.exe")
BIN_MAIN = os.path.join(ROOT_DIR, "skyscraper_solver_main.exe")
BIN_V08 = os.path.join(ROOT_DIR, "skyscraper_solver_v08.exe")
BIN_CURR = os.path.join(ROOT_DIR, "skyscraper_solver.exe")

BENCHMARK_IN = os.path.join(ROOT_DIR, "benchmark_sets", "benchmarkSet9.txt")
PATH_OUT_EASY = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated.txt")
PATH_OUT_HARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated_harder.txt")

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
    for name, bin_path in [("dev", BIN_DEV), ("main", BIN_MAIN), ("v08", BIN_V08), ("current", BIN_CURR)]:
        t = run_solver(bin_path, clue, timeout=120.0)
        if t is None:
            return None
        times[name] = t
    return times

def evaluate_all_symmetries(clue, timeout=120.0):
    rots = get_symmetries(clue)
    tasks = []
    for rot in rots:
        for name, bin_path in [("dev", BIN_DEV), ("main", BIN_MAIN), ("v08", BIN_V08), ("current", BIN_CURR)]:
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
    for path in [BIN_DEV, BIN_MAIN, BIN_V08, BIN_CURR]:
        if not os.path.exists(path):
            print(f"Error: Binary {path} not found. Please compile it first.")
            sys.exit(1)
            
    print(f"Loading candidate puzzles from {BENCHMARK_IN}...")
    with open(BENCHMARK_IN, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]
        
    print(f"Loaded {len(lines)} raw puzzles.")
    
    candidates = {}
    
    # Phase 1: Filter base clues (under 120s)
    print("Phase 1: Broad Base-Clue Filtering...")
    
    max_workers = 8
    # We scan a chunk of 3000 puzzles (lines 2000 to 5000)
    scan_start = 2000
    scan_end = 5000
    chunk = lines[scan_start:scan_end]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(evaluate_base_clue, clue): clue for clue in chunk}
        
        for i, fut in enumerate(concurrent.futures.as_completed(futures)):
            clue = futures[fut]
            times = fut.result()
            
            if times is not None:
                key = canonize(clue)
                if key not in candidates:
                    candidates[key] = clue
                        
            if (i + 1) % 500 == 0:
                print(f"  Processed {i+1}/{len(chunk)} base clues... Candidates: {len(candidates)}")
                
    print(f"Base Clue Filtering complete. Found {len(candidates)} unique candidates.")
    
    # Phase 2: Symmetry Verification and Classification
    print("\nPhase 2: Symmetry Verification & Classification (120s timeout)...")
    
    verified_easy = []
    verified_hard = []
    
    candidate_keys = list(candidates.keys())
    for count, key in enumerate(candidate_keys):
        clue = candidates[key]
        t_max = evaluate_all_symmetries(clue, timeout=120.0)
        
        if t_max is not None:
            if t_max >= 2.0:
                if len(verified_hard) < 55:
                    verified_hard.append(clue)
                    print(f"  [HARD] {len(verified_hard)}/50 Verified: t_max = {t_max:.2f}s (Base: {clue[:20]}...)")
            else:
                if len(verified_easy) < 105:
                    verified_easy.append(clue)
                    print(f"  [EASY] {len(verified_easy)}/100 Verified: t_max = {t_max:.2f}s (Base: {clue[:20]}...)")
                    
        # Early stop if we have enough of both
        if len(verified_easy) >= 100 and len(verified_hard) >= 50:
            print("Successfully verified target counts for both sets!")
            break
            
        if (count + 1) % 50 == 0:
            print(f"  Checked {count+1}/{len(candidate_keys)} candidates... (Easy: {len(verified_easy)}, Hard: {len(verified_hard)})")
            
    print(f"\nVerification complete. Easy verified: {len(verified_easy)}, Hard verified: {len(verified_hard)}")
    
    if len(verified_easy) < 100:
        print(f"Warning: Only verified {len(verified_easy)} easy puzzles (target 100).")
    if len(verified_hard) < 50:
        print(f"Warning: Only verified {len(verified_hard)} hard puzzles (target 50).")
        
    # Expand and save easy puzzles
    easy_expanded = []
    for clue in verified_easy[:100]:
        easy_expanded.extend(get_symmetries(clue))
    easy_expanded = list(dict.fromkeys(easy_expanded))
    
    os.makedirs(os.path.dirname(PATH_OUT_EASY), exist_ok=True)
    with open(PATH_OUT_EASY, "w") as f:
        for clue in easy_expanded:
            f.write(f'"{clue}"\n')
    print(f"Wrote {len(easy_expanded)} easy symmetric variants (100 unique base puzzles) to {PATH_OUT_EASY}")
    
    # Expand and save hard puzzles
    hard_expanded = []
    for clue in verified_hard[:50]:
        hard_expanded.extend(get_symmetries(clue))
    hard_expanded = list(dict.fromkeys(hard_expanded))
    
    os.makedirs(os.path.dirname(PATH_OUT_HARD), exist_ok=True)
    with open(PATH_OUT_HARD, "w") as f:
        for clue in hard_expanded:
            f.write(f'"{clue}"\n')
    print(f"Wrote {len(hard_expanded)} hard symmetric variants (50 unique base puzzles) to {PATH_OUT_HARD}")
    
    print("\nSize 9 Dataset Calibration Completed Successfully!")

if __name__ == "__main__":
    main()
