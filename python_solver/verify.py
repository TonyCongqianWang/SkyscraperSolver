"""Bounded exhaustive CLI verification against stored independent counts."""
import argparse
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def verify_dataset(backend, puzzles, expected, case_timeout=10, deadline=None):
    rows = [row.strip() for row in puzzles.read_text().splitlines() if row.strip()]
    counts = [int(row) for row in expected.read_text().splitlines() if row.strip()]
    if not rows or len(rows) != len(counts):
        raise ValueError(f"{puzzles}: empty set or mismatched count file")
    started = time.monotonic()
    slowest = 0
    for index, (row, count) in enumerate(zip(rows, counts), 1):
        remaining = deadline - time.monotonic() if deadline else case_timeout
        if remaining <= 0:
            raise RuntimeError("Total verification time budget exceeded")
        args = shlex.split(row) if row.startswith(('"', "'")) else [row]
        before = time.monotonic()
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT / "python_solver/solve_sky.py"),
                 "-b", backend, "-s", "0", *args],
                capture_output=True, text=True,
                timeout=min(case_timeout, remaining))
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(f"{puzzles.name} row {index}: exceeded "
                               f"{min(case_timeout, remaining):.1f}s") from error
        elapsed = time.monotonic() - before
        slowest = max(slowest, elapsed)
        match = re.search(r"Total Unique Solutions Found: (\d+)", result.stdout)
        actual = int(match[1]) if match else (
            0 if "UNSATISFIABLE (No Solution Found)" in result.stdout else None)
        if result.returncode or actual != count:
            raise RuntimeError(f"{puzzles.name} row {index}: expected {count}, "
                               f"got {actual}; exit {result.returncode}; {result.stderr}")
    elapsed = time.monotonic() - started
    print(f"{backend} {puzzles.name}: {len(rows)}/{len(rows)} passed; "
          f"total {elapsed:.2f}s; slowest {slowest:.2f}s", flush=True)
    return elapsed, slowest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("z3", "cpsat"), required=True)
    parser.add_argument("--dataset", nargs=2, action="append", metavar=("PUZZLES", "COUNTS"))
    parser.add_argument("--case-timeout", type=float, default=10)
    parser.add_argument("--total-timeout", type=float, default=180)
    args = parser.parse_args()
    if args.case_timeout <= 0 or args.total_timeout <= 0:
        parser.error("Timeouts must be positive")
    datasets = args.dataset or [
        [f"benchmark_sets/benchmarkSet{size}_python20.txt",
         f"benchmark_sets/_num_solutions_benchmarkSet{size}_python20.txt"]
        for size in (7, 8)
    ] + [["benchmark_sets/benchmarkSet9_minimal20.txt",
          "benchmark_sets/_num_solutions_benchmarkSet9_minimal20.txt"]]
    started = time.monotonic()
    deadline = started + args.total_timeout
    try:
        for puzzles, counts in datasets:
            verify_dataset(args.backend, ROOT / puzzles, ROOT / counts,
                           args.case_timeout, deadline)
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f"Verification failed: {error}\n")
    print(f"{args.backend}: total verification {time.monotonic() - started:.2f}s")


if __name__ == "__main__":
    main()
