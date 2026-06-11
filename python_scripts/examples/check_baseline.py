#!/usr/bin/env python3
import subprocess
import os

SIZE8_FILE = "benchmark_sets/benchmarkSet8_easy50.txt"
SIZE7_FILE = "benchmark_sets/benchmarkSet7_easy500.txt"

def load_instances(filepath):
    with open(filepath, "r") as f:
        return [line.strip().strip('"') for line in f if line.strip()]

def run_solver(binary, options, clues):
    cmd = [binary] + options.split() + [clues]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    nodes = None
    for line in proc.stdout.splitlines():
        if line.startswith("Nodes visited:"):
            nodes = int(line.split(":")[1].strip())
    return nodes

def main():
    s7_subset = load_instances(SIZE7_FILE)
    s8_subset = load_instances(SIZE8_FILE)
    
    s7_nodes = sum(run_solver("./skyscraper_solver", "-s 0", clues) for clues in s7_subset)
    s8_nodes = sum(run_solver("./skyscraper_solver", "-s 1", clues) for clues in s8_subset)
    
    print(f"Current Solver -> S7: {s7_nodes:,}, S8: {s8_nodes:,}, Total: {s7_nodes+s8_nodes:,}")

if __name__ == "__main__":
    main()
