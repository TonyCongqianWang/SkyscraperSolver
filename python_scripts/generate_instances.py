#!/usr/bin/env python3
import time
import argparse
import os
import sys
import random
import numpy as np
from numba import njit

def generate_random_latin_square(n):
    """
    Generates a random Latin square of size N using a simple randomized backtracking search.
    This provides an unbiased starting grid for the MCMC chain.
    """
    grid = [[0]*n for _ in range(n)]
    
    def solve(r, c):
        if r == n:
            return True
        next_r, next_c = (r, c + 1) if c + 1 < n else (r + 1, 0)
        
        used = set(grid[r][i] for i in range(c)) | set(grid[i][c] for i in range(r))
        allowed = [s for s in range(1, n + 1) if s not in used]
        random.shuffle(allowed)
        
        for s in allowed:
            grid[r][c] = s
            if solve(next_r, next_c):
                return True
            grid[r][c] = 0
        return False

    solve(0, 0)
    return np.array(grid, dtype=np.int32) - 1


@njit
def generate_uniform_latin_squares(n, count, start_grid, burn_in=100000, gap=100):
    """
    Generates a uniform distribution of Latin squares starting from start_grid
    using the Cycle Switch (Kempe Chain) MCMC algorithm.
    """
    # The tensor to hold the final extracted squares
    results = np.zeros((count, n, n), dtype=np.int32)
    grid = start_grid.copy()

    # Pre-allocate flat cycle buffers
    cycle_r = np.zeros(n, dtype=np.int32)
    cycle_c_s1 = np.zeros(n, dtype=np.int32)
    cycle_c_s2 = np.zeros(n, dtype=np.int32)

    total_steps = burn_in + count * gap
    samples_taken = 0
    steps_since_last = 0
    is_burn_in = (burn_in > 0)

    for step in range(total_steps):
        # Pick a random starting cell and a random target symbol
        r = np.random.randint(0, n)
        c = np.random.randint(0, n)
        s_1 = grid[r, c]
        s_2 = np.random.randint(0, n)

        # If the symbols are different, trace and swap the alternating cycle
        if s_1 != s_2:
            start_r = r
            curr_r = r
            curr_c = c
            cycle_len = 0

            # Trace the cycle of s_1 and s_2 without mutating the grid yet
            while True:
                # Find where s_2 is in the current row
                next_c = -1
                for i in range(n):
                    if grid[curr_r, i] == s_2:
                        next_c = i
                        break

                # Find where s_1 is in that target column
                next_r = -1
                for i in range(n):
                    if grid[i, next_c] == s_1:
                        next_r = i
                        break

                # Log the cycle coordinates
                cycle_r[cycle_len] = curr_r
                cycle_c_s1[cycle_len] = curr_c
                cycle_c_s2[cycle_len] = next_c
                cycle_len += 1

                # If the cycle loops back to the starting row, the trace is complete
                if next_r == start_r:
                    break

                curr_r = next_r
                curr_c = next_c

            # Apply the structural flip across the entire cycle simultaneously
            for i in range(cycle_len):
                grid[cycle_r[i], cycle_c_s1[i]] = s_2
                grid[cycle_r[i], cycle_c_s2[i]] = s_1

        # MCMC Sampling
        if is_burn_in:
            if step == burn_in - 1:
                is_burn_in = False
        else:
            steps_since_last += 1
            if steps_since_last == gap:
                # Extract the matrix, converting to 1-indexed numbers (1 to N)
                for i in range(n):
                    for j in range(n):
                        results[samples_taken, i, j] = grid[i, j] + 1
                
                samples_taken += 1
                steps_since_last = 0
                if samples_taken == count:
                    break

    return results, grid


@njit
def extract_clues_batch(squares):
    """
    Extracts top, bottom, left, and right skyscraper visibility clues for a batch of grids.
    """
    count = squares.shape[0]
    n = squares.shape[1]
    T = np.zeros((count, n), dtype=np.int32)
    B = np.zeros((count, n), dtype=np.int32)
    L = np.zeros((count, n), dtype=np.int32)
    R = np.zeros((count, n), dtype=np.int32)
    
    for i in range(count):
        grid = squares[i]
        # Top/Bottom clues
        for c in range(n):
            # Top clue
            val_t = 0
            max_t = 0
            for r in range(n):
                h = grid[r, c]
                if h > max_t:
                    max_t = h
                    val_t += 1
            T[i, c] = val_t
            
            # Bottom clue
            val_b = 0
            max_b = 0
            for r in range(n - 1, -1, -1):
                h = grid[r, c]
                if h > max_b:
                    max_b = h
                    val_b += 1
            B[i, c] = val_b
            
        # Left/Right clues
        for r in range(n):
            # Left clue
            val_l = 0
            max_l = 0
            for c in range(n):
                h = grid[r, c]
                if h > max_l:
                    max_l = h
                    val_l += 1
            L[i, r] = val_l
            
            # Right clue
            val_r = 0
            max_r = 0
            for c in range(n - 1, -1, -1):
                h = grid[r, c]
                if h > max_r:
                    max_r = h
                    val_r += 1
            R[i, r] = val_r
            
    return T, B, L, R


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from symmetry import canonize_one


def generate_unique_instances(n, target_count, burn_in=100000, gap=100):
    """
    Generates target_count unique (under symmetry) instances of size N.
    """
    seen_canonized = set()
    unique_clues = []
    
    print(f"Generating {target_count} unique symmetric variants for size {n}x{n}...")
    start_time = time.perf_counter()
    
    # Initialize the continuous chain starting grid
    start_grid = generate_random_latin_square(n)
    
    consecutive_no_additions = 0
    consecutive_reseeds_with_no_additions = 0
    current_burn_in = burn_in
    
    while len(unique_clues) < target_count:
        remaining = target_count - len(unique_clues)
        # Generate slightly more than remaining to cover any collision
        curr_batch_size = max(2000, int(remaining * 1.05))
        
        print(f"  MCMC generating batch of {curr_batch_size} Latin squares...")
        squares, start_grid = generate_uniform_latin_squares(
            n=n, count=curr_batch_size, start_grid=start_grid, burn_in=current_burn_in, gap=gap
        )
        # For subsequent batches in this loop, we set burn_in to 0 because we are
        # continuing the chain
        current_burn_in = 0
        
        print(f"  Extracting clues...")
        T, B, L, R = extract_clues_batch(squares)
        
        print(f"  Filtering for symmetry-uniqueness...")
        added_in_batch = 0
        for i in range(curr_batch_size):
            key = canonize_one(T[i], B[i], L[i], R[i])
            if key not in seen_canonized:
                seen_canonized.add(key)
                clue_str = " ".join(map(str, T[i])) + " " + " ".join(map(str, B[i])) + " " + " ".join(map(str, L[i])) + " " + " ".join(map(str, R[i]))
                unique_clues.append(clue_str)
                added_in_batch += 1
                if len(unique_clues) == target_count:
                    break
        
        print(f"  Progress: {len(unique_clues)}/{target_count} unique clues found (+{added_in_batch} this batch).")
        
        if added_in_batch == 0:
            consecutive_no_additions += 1
            if consecutive_no_additions >= 2:
                # Re-seed the MCMC chain from a new random backtracking Latin square
                print(f"  MCMC chain trapped or exhausted. Re-seeding from a new random Latin square...")
                start_grid = generate_random_latin_square(n)
                current_burn_in = burn_in
                consecutive_no_additions = 0
                consecutive_reseeds_with_no_additions += 1
                if consecutive_reseeds_with_no_additions >= 5:
                    print(f"  Warning: No new unique clues found after 5 consecutive re-seeds. We have likely exhausted all possible unique configurations in the entire state space of size {n}.")
                    break
        else:
            consecutive_no_additions = 0
            consecutive_reseeds_with_no_additions = 0
        
    elapsed = time.perf_counter() - start_time
    print(f"Generation completed in {elapsed:.2f}s.")
    return unique_clues


def main():
    parser = argparse.ArgumentParser(description="Generate Skyscraper puzzle instances of arbitrary sizes.")
    parser.add_argument("-n", "--size", type=int, required=True, help="Board size (N x N)")
    parser.add_argument("-c", "--count", type=int, default=10000, help="Number of unique instances to generate")
    parser.add_argument("-o", "--output", type=str, required=True, help="Non-optional output file path")
    parser.add_argument("--burn-in", type=int, default=100000, help="Burn-in steps for MCMC")
    parser.add_argument("--gap", type=int, default=100, help="Gap between samples in MCMC")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    # Generate instances
    clues = generate_unique_instances(
        n=args.size,
        target_count=args.count,
        burn_in=args.burn_in,
        gap=args.gap
    )
    
    # Save clues in double-quoted benchmark format
    print(f"Saving clues to {args.output}...")
    with open(args.output, "w") as f:
        for clue in clues:
            f.write(f'"{clue}"\n')
            
    print(f"Successfully saved {len(clues)} instances.")

if __name__ == "__main__":
    main()
