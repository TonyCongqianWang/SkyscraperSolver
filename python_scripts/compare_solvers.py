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
    # Accept one or more benchmark files
    parser.add_argument("benchmark_files", nargs="+", help="List of benchmark files to process")
    parser.add_argument("-r", "--compare", default="./skyscraper_solver_compare")
    parser.add_argument("-b", "--baseline", default="./skyscraper_solver_baseline")
    parser.add_argument("-o", "--options", default="-s 1")
    parser.add_argument("-n", "--num_instances", type=int, default=None)
    args = parser.parse_args()

    print(f"Compare: {args.compare}")
    print(f"Baseline:   {args.baseline}")
    print(f"Options:    {args.options}")
    print("=" * 50)

    for benchmark_file in args.benchmark_files:
        if not os.path.exists(benchmark_file):
            print(f"\nError: File {benchmark_file} not found. Skipping.\n" + "=" * 50, file=sys.stderr)
            continue

        with open(benchmark_file, "r") as f:
            lines = [line.strip().strip('"') for line in f if line.strip()]

        if args.num_instances is not None:
            lines = lines[:args.num_instances]

        print(f"\nEvaluating benchmark file: {benchmark_file} ({len(lines)} instances)")
        print("-" * 50)

        # Reset counters for each file to prevent aggregation
        ref_total_nodes = 0
        ref_total_time = 0.0
        base_total_nodes = 0
        base_total_time = 0.0

        for idx, clues in enumerate(lines, start=1):
            res_ref = run_solver(args.compare, args.options, clues)
            res_base = run_solver(args.baseline, args.options, clues)

            if "error" in res_ref or "error" in res_base:
                print(f"Instance {idx} error: ref={res_ref.get('error')}, base={res_base.get('error')}", file=sys.stderr)
                continue

            ref_total_nodes += res_ref["nodes"]
            ref_total_time += res_ref["time"]
            base_total_nodes += res_base["nodes"]
            base_total_time += res_base["time"]

        print(f"Compare total nodes:  {ref_total_nodes}")
        print(f"Baseline total nodes:   {base_total_nodes}")
        node_red = (base_total_nodes - ref_total_nodes) / base_total_nodes * 100 if base_total_nodes else 0
        print(f"Node Reduction:         {node_red:.2f}%")
        print("-" * 50)
        print(f"Compare total time:  {ref_total_time:.3f}s")
        print(f"Baseline total time:    {base_total_time:.3f}s")
        time_red = (base_total_time - ref_total_time) / base_total_time * 100 if base_total_time else 0
        print(f"Speedup:                {time_red:.2f}%")
        print("=" * 50)

if __name__ == "__main__":
    main()
