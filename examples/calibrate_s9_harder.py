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
BENCHMARK_OUT = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated_harder.txt")

TARGET_COUNT = 12
START_LINE = 3500
END_LINE = 9500

def get_rotations(clue_str):
    nums = list(map(int, clue_str.split()))
    n = len(nums) // 4
    T = nums[0:n]
    B = nums[n:2*n]
    L = nums[2*n:3*n]
    R = nums[3*n:4*n]
    
    # 0 degrees
    r0 = T + B + L + R
    # 90 degrees clockwise
    r90 = L[::-1] + R[::-1] + B + T
    # 180 degrees
    r180 = B[::-1] + T[::-1] + R[::-1] + L[::-1]
    # 270 degrees clockwise
    r270 = R + L + T[::-1] + B[::-1]
    
    rots = [
        " ".join(map(str, r0)),
        " ".join(map(str, r90)),
        " ".join(map(str, r180)),
        " ".join(map(str, r270))
    ]
    return list(dict.fromkeys(rots))

def run_solver(binary, clue, timeout=30.0):
    t_start = time.perf_counter()
    try:
        proc = subprocess.run(
            [binary, "-s", "1", clue],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        elapsed = time.perf_counter() - t_start
        if proc.returncode != 0:
            return None
        return elapsed
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None

def evaluate_puzzle(clue):
    # 1. Evaluate base clue first
    times = {}
    for name, bin_path in [("dev", BIN_DEV), ("main", BIN_MAIN), ("v08", BIN_V08), ("current", BIN_CURR)]:
        t = run_solver(bin_path, clue, timeout=15.0)
        if t is None:
            return None
        times[name] = t
        
    # Base clue must take between 0.4s and 15.0s on all binaries
    for t in times.values():
        if t < 0.4 or t > 15.0:
            return None
            
    # 2. Check all rotations/orientations on all binaries to make sure they solve in under 30.0s
    rots = get_rotations(clue)
    for rot in rots:
        for name, bin_path in [("dev", BIN_DEV), ("main", BIN_MAIN), ("v08", BIN_V08), ("current", BIN_CURR)]:
            t = run_solver(bin_path, rot, timeout=30.0)
            if t is None or t > 30.0:
                return None
                
    return times

def main():
    if not os.path.exists(BENCHMARK_IN):
        print(f"Error: {BENCHMARK_IN} not found.")
        sys.exit(1)
        
    for path in [BIN_DEV, BIN_MAIN, BIN_V08, BIN_CURR]:
        if not os.path.exists(path):
            print(f"Error: Binary {path} not found. Please compile it first.")
            sys.exit(1)

    print(f"Loading candidate puzzles from {BENCHMARK_IN}...")
    with open(BENCHMARK_IN, "r") as f:
        lines = [line.strip().strip('"') for line in f if line.strip()]

    # We append the one we already found on line 3417 to ensure it is kept
    existing_hard = "5 3 2 1 2 2 4 4 1 2 3 4 5 2 2 1 2 4 3 2 2 3 1 4 2 2 2 1 2 5 3 2 3 3 1 2"
    calibrated_puzzles = [existing_hard]

    candidates = lines[START_LINE:END_LINE]
    print(f"Scanning lines {START_LINE} to {END_LINE} for {TARGET_COUNT} harder calibrated puzzles...")
    
    max_workers = 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(evaluate_puzzle, line): (idx, line) for idx, line in enumerate(candidates, START_LINE + 1)}
        
        count = len(calibrated_puzzles)
        for i, fut in enumerate(concurrent.futures.as_completed(futures)):
            line_num, clue = futures[fut]
            times = fut.result()
            
            if times is not None:
                calibrated_puzzles.append(clue)
                count += 1
                times_str = ", ".join([f"{k}: {v:.2f}s" for k, v in times.items()])
                print(f"Found harder match {count}/{TARGET_COUNT} (Line {line_num}): {times_str}")
                if count >= TARGET_COUNT:
                    break
            
            if (i + 1) % 200 == 0:
                print(f"Processed {i+1}/{len(futures)} candidates...")
                
    if len(calibrated_puzzles) < TARGET_COUNT:
        print(f"Warning: Only found {len(calibrated_puzzles)} calibrated puzzles.")
        
    print(f"Generating rotations for {len(calibrated_puzzles)} puzzles...")
    all_calib_clues = []
    for clue in calibrated_puzzles:
        rots = get_rotations(clue)
        all_calib_clues.extend(rots)
        
    all_calib_clues = list(dict.fromkeys(all_calib_clues))
    
    print(f"Writing {len(all_calib_clues)} total clues (including rotated variants) to {BENCHMARK_OUT}...")
    os.makedirs(os.path.dirname(BENCHMARK_OUT), exist_ok=True)
    with open(BENCHMARK_OUT, "w") as f:
        for clue in all_calib_clues:
            f.write(f'"{clue}"\n')
            
    print("Calibration of harder set completed successfully!")

if __name__ == "__main__":
    main()
