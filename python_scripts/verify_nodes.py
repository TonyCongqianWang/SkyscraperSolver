#!/usr/bin/env python3
import subprocess
import sys
import os

def run_solver(binary, options, clues):
    cmd = [binary] + options + [clues]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15.0)
    except Exception as e:
        return {"error": f"Failed to execute: {e}"}
    if proc.returncode != 0:
        return {"error": f"Exit code {proc.returncode}. Stderr: {proc.stderr.strip()}"}
    
    nodes_visited = None
    for line in proc.stdout.splitlines():
        if line.startswith("Nodes visited:"):
            try:
                nodes_visited = int(line.split(":")[1].strip())
            except ValueError:
                pass
            break
    if nodes_visited is None:
        return {"error": f"Could not find nodes visited in output: {proc.stdout}"}
    return {"nodes": nodes_visited}

def run_test_set(bin_ref, bin_cand, file_path, label, count):
    print(f"\nEvaluating {label} ({count} instances from {file_path})...")
    print("-" * 60)
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False
        
    with open(file_path, "r") as f:
        clues = [line.strip().strip('"') for line in f if line.strip()][:count]
        
    mismatches = 0
    for idx, clue in enumerate(clues, 1):
        res_ref = run_solver(bin_ref, ["-s", "1"], clue)
        res_cand = run_solver(bin_cand, ["-s", "1"], clue)
        
        if "error" in res_ref:
            print(f"Error running reference on instance {idx}: {res_ref['error']}")
            return False
        if "error" in res_cand:
            print(f"Error running candidate on instance {idx}: {res_cand['error']}")
            return False
            
        n_ref = res_ref["nodes"]
        n_cand = res_cand["nodes"]
        
        if n_ref != n_cand:
            print(f"[MISMATCH] Instance {idx}: Ref = {n_ref}, Cand = {n_cand}")
            mismatches += 1
        else:
            print(f"[OK] Instance {idx}: Nodes visited = {n_ref}")
            
    print(f"Set {label} complete. Mismatches = {mismatches}")
    return mismatches == 0

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 verify_nodes.py <binary_ref> <binary_cand>")
        sys.exit(1)
        
    bin_ref = os.path.abspath(sys.argv[1])
    bin_cand = os.path.abspath(sys.argv[2])
    
    print(f"Comparing reference: {bin_ref}")
    print(f"With candidate:      {bin_cand}")
    print("-" * 60)
    
    sets = [
        ("puzzle_bank/puzzle_bank7.txt", "Size 7 Puzzles", 20),
        ("puzzle_bank/puzzle_bank8.txt", "Size 8 Puzzles", 20),
        ("benchmark_sets/benchmarkSet9_small.txt", "Size 9 Puzzles (Small Set)", 20)
    ]
    
    all_success = True
    for file_path, label, count in sets:
        # Resolve path relative to repository root if not absolute
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file_path)
        success = run_test_set(bin_ref, bin_cand, file_path, label, count)
        if not success:
            all_success = False
            
    print("-" * 60)
    if all_success:
        print("SUCCESS: Both binaries matched exactly on all sets!")
        sys.exit(0)
    else:
        print("FAILURE: Mismatches were found in one or more sets!")
        sys.exit(1)

if __name__ == "__main__":
    main()
