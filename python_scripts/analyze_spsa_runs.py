#!/usr/bin/env python3
import glob
import re
import numpy as np
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from param_metadata import PARAM_METADATA

DEFAULTS = {p[0]: p[3] for p in PARAM_METADATA}

def parse_run_file(filepath):
    size = None
    tune_mode = "unknown"
    pdict = {}
    
    with open(filepath, "r") as f:
        for line in f:
            m_hdr = re.search(r'SIZE\s+(\d+)', line, re.IGNORECASE)
            if m_hdr and size is None:
                size = int(m_hdr.group(1))
            if "strategy" in line.lower():
                tune_mode = "strategy"
            elif "math" in line.lower():
                tune_mode = "math"
                
            m = re.match(r'^\s*(?:#define\s+)?([A-Z0-9_]+)\s*[:=]?\s*([0-9.eE+-]+)\s*$', line)
            if m:
                pdict[m.group(1)] = float(m.group(2))
                
    return size, tune_mode, pdict

def main():
    parser = argparse.ArgumentParser(description="Analyze SPSA run text files with size-aware parameter filtering and statistical noise estimation.")
    parser.add_argument("files", nargs="*", help="Paths to run text files (e.g. scratch/run_*.txt). If omitted, defaults to scratch/run_*.txt")
    parser.add_argument("--size", type=int, choices=[7, 8, 9], default=None, help="Filter analysis to a specific puzzle size")
    args = parser.parse_args()

    if args.files:
        run_files = []
        for f in args.files:
            run_files.extend(glob.glob(f))
    else:
        run_files = sorted(glob.glob(os.path.join(ROOT_DIR, "scratch", "run_*.txt")))

    if not run_files:
        print("No run files found to analyze.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(run_files)} SPSA run file(s) for analysis.\n")

    size_runs = {7: [], 8: [], 9: [], 'unknown': []}
    for rf in run_files:
        sz, mode, pdict = parse_run_file(rf)
        target_size = sz if sz in [7, 8, 9] else 'unknown'
        size_runs[target_size].append((os.path.basename(rf), mode, pdict))

    sizes_to_analyze = [args.size] if args.size else [7, 8, 9]

    for s in sizes_to_analyze:
        runs = size_runs.get(s, [])
        if not runs:
            continue

        print("=" * 125)
        print(f"SPSA PARAMETER ANALYSIS: PUZZLE SIZE {s} ({len(runs)} RUNS)")
        print("=" * 125)

        # Collect all parameter keys present in these runs that belong to this size or are general
        all_keys = set()
        for _, _, pdict in runs:
            all_keys.update(pdict.keys())

        # Filter keys: keep keys that either end in _S{s} or don't end in _S7/_S8/_S9
        size_filtered_keys = []
        for k in sorted(all_keys):
            if any(k.endswith(f"_S{other_s}") for other_s in [7, 8, 9] if other_s != s):
                continue
            size_filtered_keys.append(k)

        print(f"{'PARAMETER NAME':<42} | {'DEFAULT':<10} | {'MEDIAN':<10} | {'MEAN':<10} | {'STD (σ)':<8} | {'RSD %':<7} | {'SHIFT %':<8} | {'SIGNAL EVALUATION'}")
        print("-" * 125)

        for k in size_filtered_keys:
            vals = [pdict[k] for _, _, pdict in runs if k in pdict]
            if not vals:
                continue
            arr = np.array(vals)
            med = float(np.median(arr))
            mean = float(np.mean(arr))
            std = float(np.std(arr))
            start_val = DEFAULTS.get(k, med)

            rsd = (std / abs(mean) * 100.0) if mean != 0 else 0.0
            shift_pct = ((med - start_val) / abs(start_val) * 100.0) if start_val != 0 else 0.0
            shift_mag = abs(med - start_val)
            s_ratio = (shift_mag / std) if std > 1e-6 else (99.0 if shift_mag > 1e-6 else 0.0)

            if s_ratio >= 2.0 and abs(shift_pct) >= 2.0:
                sig_eval = f"STRONG SIGNAL (SNR: {s_ratio:.1f}x)"
            elif s_ratio >= 1.0 or abs(shift_pct) >= 1.0:
                sig_eval = f"MODERATE SIGNAL (SNR: {s_ratio:.1f}x)"
            else:
                sig_eval = "FLAT / NOISE"

            if "RATIO" in k or "SCALE" in k or "ENTROPY" in k or "MIN" in k or "MAX" in k:
                if isinstance(start_val, int) or start_val > 10.0:
                    med_fmt = f"{int(round(med))}"
                    mean_fmt = f"{mean:.2f}"
                    start_fmt = f"{int(round(start_val))}" if isinstance(start_val, (int, float)) else f"{start_val}"
                else:
                    med_fmt = f"{med:.4f}"
                    mean_fmt = f"{mean:.4f}"
                    start_fmt = f"{start_val:.4f}"
            else:
                med_fmt = f"{med:.4f}"
                mean_fmt = f"{mean:.4f}"
                start_fmt = f"{start_val:.4f}"

            print(f"{k:<42} | {start_fmt:<10} | {med_fmt:<10} | {mean_fmt:<10} | {std:<8.2f} | {rsd:<7.2f}% | {shift_pct:+7.2f}% | {sig_eval}")

        print("\n")

if __name__ == "__main__":
    main()
