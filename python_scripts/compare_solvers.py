#!/usr/bin/env python3
import subprocess
import sys
import time
import argparse
import os

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark_files", nargs="+", help="List of benchmark files to process")
    parser.add_argument("-r", "--refactored", default="./skyscraper_solver")
    parser.add_argument("-b", "--baseline", default="./skyscraper_solver_main")
    # Changed to nargs="+" with a default list containing the default string
    parser.add_argument("-o", "--options", nargs="+", default=["-s 1"])
    parser.add_argument("-n", "--num_instances", type=int, default=None)
    args = parser.parse_args()

    num_files = len(args.benchmark_files)
    num_options = len(args.options)

    # Validate the length of the options list
    if num_options != 1 and num_options != num_files:
        print(
            f"Error: Number of options ({num_options}) must match either 1 "
            f"or the number of benchmark files ({num_files}).",
            file=sys.stderr
        )
        sys.exit(1)

    print(f"Refactored: {args.refactored}")
    print(f"Baseline:   {args.baseline}")
    print("=" * 50)

    for idx, benchmark_file in enumerate(args.benchmark_files):
        if not os.path.exists(benchmark_file):
            print(f"\nError: File {benchmark_file} not found. Skipping.\n" + "=" * 50, file=sys.stderr)
            continue

        # Determine which option string to use for this specific file
        current_options = args.options[0] if num_options == 1 else args.options[idx]

        with open(benchmark_file, "r") as f:
            lines = [line.strip().strip('"') for line in f if line.strip()]

        if args.num_instances is not None:
            lines = lines[:args.num_instances]

        print(f"\nEvaluating benchmark file: {benchmark_file} ({len(lines)} instances)")
        print(f"Options used:             {current_options}")
        print("-" * 50)

        ref_total_nodes = 0
        ref_total_time = 0.0
        base_total_nodes = 0
        base_total_time = 0.0

        for inst_idx, clues in enumerate(lines, start=1):
            res_ref = run_solver(args.refactored, current_options, clues)
            res_base = run_solver(args.baseline, current_options, clues)

            if "error" in res_ref or "error" in res_base:
                print(f"Instance {inst_idx} error: ref={res_ref.get('error')}, base={res_base.get('error')}", file=sys.stderr)
                continue

            ref_total_nodes += res_ref["nodes"]
            ref_total_time += res_ref["time"]
            base_total_nodes += res_base["nodes"]
            base_total_time += res_base["time"]

        print(f"Refactored total nodes: {ref_total_nodes}")
        print(f"Baseline total nodes:   {base_total_nodes}")
        node_red = (base_total_nodes - ref_total_nodes) / base_total_nodes * 100 if base_total_nodes else 0
        print(f"Node Reduction:         {node_red:.2f}%")
        print("-" * 50)
        print(f"Refactored total time:  {ref_total_time:.3f}s")
        print(f"Baseline total time:    {base_total_time:.3f}s")
        time_red = (base_total_time - ref_total_time) / base_total_time * 100 if base_total_time else 0
        print(f"Speedup:                {time_red:.2f}%")
        print("=" * 50)

if __name__ == "__main__":
    main()
