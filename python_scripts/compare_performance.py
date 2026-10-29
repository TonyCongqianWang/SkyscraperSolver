#!/usr/bin/env python3
import os
import sys
import argparse
import json
import statistics
from contextlib import ExitStack

from comparison_measurements import measure_batch
from param_metadata import PARAM_METADATA
from spsa_metrics import get_sgm_shifts, shifted_geo_mean
from spsa_run_metadata import clue_identity
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

BIN_BASELINE = os.path.join(ROOT_DIR, "skyscraper_solver_main")
BIN_TUNABLE = os.path.join(ROOT_DIR, "skyscraper_solver")

# Paths to datasets
PATH_S7 = os.path.join(ROOT_DIR, "puzzle_bank", "puzzle_bank7.txt")

# Size 8 calibrated files
PATH_S8_EASY = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_easy.txt")
PATH_S8_MED = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_medium.txt")
PATH_S8_HARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_hard.txt")
PATH_S8_XHARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_xhard.txt")

# Size 9 calibrated files
PATH_S9 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated.txt")
PATH_S9_HARDER = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated_harder.txt")

def resolve_binary_path(path):
    if path and (os.name == 'nt' or sys.platform.startswith('win')):
        if not path.lower().endswith('.exe') and os.path.exists(path + '.exe'):
            return path + '.exe'
    return path


def default_environment():
    # A default comparison must not inherit stale tuning overrides.
    env = os.environ.copy()
    for name, *_ in PARAM_METADATA:
        env.pop(name, None)
    return env


def summarize(rows, shifts):
    time_shift, node_shift = shifts
    return {
        'total_nodes': sum(row['nodes'] for row in rows),
        'total_time': sum(row['seconds'] for row in rows),
        'sgm_nodes': shifted_geo_mean([row['nodes'] for row in rows], node_shift),
        'sgm_time': shifted_geo_mean([row['seconds'] for row in rows], time_shift),
    }


def evaluate_set(clues, opt, label, baseline_bin, tunable_bin, tuned_env=None,
                 log_print=print, use_stdin=True, max_workers=4, repeats=2,
                 warmup=1, timeout=15.0, size=None, records_file=None):
    if repeats < 1 or repeats % 2:
        raise ValueError('repeats must be a positive even number for AB/BA balance')
    if size is None:
        clue = clues[0].strip().strip('"').replace(',', ' ')
        tokens = clue.split()
        token_count = len(tokens) if len(tokens) > 1 else len(clue)
        if token_count % 4:
            raise ValueError('clue length must be divisible by four')
        size = token_count // 4
    shifts = get_sgm_shifts(size, opt.split() == ['-s', '0'])
    log_print(f"\nEvaluating {label} ({len(clues)} instances, options: '{opt}')...")
    log_print(f"SGM shifts: time={shifts[0]:g}s, nodes={shifts[1]:g}; "
              f"workers={max_workers}, repeats={repeats}, warmup={warmup}")
    base_env = default_environment()
    candidates = {
        'Baseline': (baseline_bin, base_env),
        'Optimized': (tunable_bin, tuned_env if tuned_env is not None else base_env),
    }
    rounds = []
    valid = True
    for repeat in range(repeats):
        order = ['Baseline', 'Optimized'] if repeat % 2 == 0 else ['Optimized', 'Baseline']
        measured = {}
        for position, arm in enumerate(order):
            binary, env = candidates[arm]
            measured[arm] = measure_batch(binary, opt, clues, env,
                                         workers=max_workers, use_stdin=use_stdin,
                                         warmup=warmup, timeout=timeout)
            if records_file:
                for row in measured[arm]:
                    records_file.write(json.dumps(dict(
                        row, dataset=label, size=size, options=opt,
                        repeat=repeat + 1, arm=arm, order=position + 1,
                        binary=os.path.basename(binary))) + '\n')
                records_file.flush()
        base, optimized = measured['Baseline'], measured['Optimized']
        paired = [(b, o) for b, o in zip(base, optimized)
                  if b['status'] == o['status'] == 'ok']
        mismatches = sum(b['solutions'] != o['solutions'] for b, o in paired
                         if b['solutions'] is not None and o['solutions'] is not None)
        known_counts = sum(b['solutions'] is not None and o['solutions'] is not None
                           for b, o in paired)
        failures = {arm: {status: sum(row['status'] == status for row in rows)
                          for status in ('timeout', 'error')}
                    for arm, rows in measured.items()}
        round_valid = len(paired) == len(clues) and not mismatches
        valid = valid and round_valid
        log_print(f"Repeat {repeat + 1} ({'/'.join(order)}): paired "
                  f"{len(paired)}/{len(clues)}, failures={failures}, "
                  f"solution mismatches={mismatches} (counts available: {known_counts})")
        results = {arm: summarize([pair[i] for pair in paired], shifts)
                   for i, arm in enumerate(('Baseline', 'Optimized'))}
        rounds.append({'repeat': repeat + 1, 'order': order, 'valid': round_valid,
                       'paired_count': len(paired), 'failures': failures,
                       'solution_count_pairs': known_counts,
                       'solution_mismatches': mismatches, 'results': results})
    if not valid:
        log_print('INVALID comparison: failed instances or mismatched solution counts. '
                  'Performance summary withheld; inspect per-instance records.')
        return {'label': label, 'valid': False, 'rounds': rounds}
    # Summarize per-round metrics rather than pooling multiple runs as new puzzles.
    log_print('| Metric | Baseline (median) | Optimized (median) | Median paired diff | Diff range |')
    log_print('|---|---|---|---|---|')
    summary = {}
    for key, title in [('total_nodes', 'Total Nodes'), ('sgm_nodes', 'SGM Nodes'),
                       ('total_time', 'Total Time'), ('sgm_time', 'SGM Time')]:
        b = [r['results']['Baseline'][key] for r in rounds]
        o = [r['results']['Optimized'][key] for r in rounds]
        # A zero baseline has no meaningful relative change.
        diffs = [(y - x) / x * 100 if x else None for x, y in zip(b, o)]
        available = [value for value in diffs if value is not None]
        summary[key] = {'baseline': statistics.median(b),
                        'optimized': statistics.median(o),
                        'diff_pct': statistics.median(available) if available else None,
                        'diff_range_pct': [min(available), max(available)] if available else None}
        diff_text = f"{statistics.median(available):+.3f}%" if available else 'n/a'
        range_text = f"{min(available):+.3f}% to {max(available):+.3f}%" if available else 'n/a'
        log_print(f"| **{title}** | {statistics.median(b):,.6g} | "
                  f"{statistics.median(o):,.6g} | {diff_text} | {range_text} |")
    return {'label': label, 'valid': True, 'size': size, 'options': opt,
            'dataset': clue_identity(clues), 'sgm_shifts': shifts,
            'workers': max_workers, 'warmup': warmup, 'summary': summary,
            'rounds': rounds}


def load_tuned_env(winners_path):
    tuned_env = default_environment()
    if not winners_path or not os.path.exists(winners_path):
        print(f"Warning: Winners file not found at '{winners_path}'. Running without env overrides.")
        return None
    with open(winners_path, "r") as f:
        for line in f:
            if line.startswith("#define"):
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1]
                    val = parts[2]
                    tuned_env[name] = val
    return tuned_env

def run_comparison(validation_tasks, baseline_bin, tunable_bin, tuned_env=None,
                   title="SOLVER PERFORMANCE COMPARISON", log_path=None,
                   use_stdin=True, max_workers=4, repeats=2, warmup=1,
                   timeout=15.0, size=None, records_path=None):
    """Compare fixed datasets in balanced AB/BA rounds; retain every outcome."""
    if max_workers < 1 or warmup < 0 or timeout <= 0:
        raise ValueError('workers/timeout must be positive; warmup nonnegative')
    if repeats < 1 or repeats % 2:
        raise ValueError('repeats must be positive and even')
    baseline = resolve_binary_path(baseline_bin)
    tunable = resolve_binary_path(tunable_bin)
    if records_path is None:
        records_path = (os.path.splitext(log_path)[0] + '_instances.jsonl'
                        if log_path else os.path.join(ROOT_DIR, 'scratch', 'comparison_instances.jsonl'))
    summary_path = os.path.splitext(records_path)[0] + '_summary.json'
    with ExitStack() as stack:
        log_file = None
        if log_path:
            os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
            log_file = stack.enter_context(open(log_path, 'w'))
        os.makedirs(os.path.dirname(os.path.abspath(records_path)), exist_ok=True)
        records_file = stack.enter_context(open(records_path, 'w'))

        def log_print(*args, **kwargs):
            print(*args, **kwargs)
            if log_file:
                print(*args, **kwargs, file=log_file)
                log_file.flush()

        log_print('=' * 70)
        log_print(f'   {title}   '.center(70))
        reports = []
        for label, options, clues in validation_tasks:
            if clues:
                reports.append(evaluate_set(
                    clues, options, label, baseline, tunable, tuned_env, log_print,
                    use_stdin, max_workers, repeats, warmup, timeout, size, records_file))
        with open(summary_path, 'w') as summary_file:
            json.dump(reports, summary_file, indent=2)
            summary_file.write('\n')
        log_print(f'Per-instance records: {records_path}')
        log_print(f'Comparison summaries: {summary_path}')
        log_print('=' * 70)
        return reports


def read_clues(file_path):
    if not os.path.exists(file_path):
        print(f"Error: dataset file not found at {file_path}", file=sys.stderr)
        return []
    with open(file_path, "r") as f:
        return [line.strip().strip('"') for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description="Compare performance of solver binaries.")
    parser.add_argument("-b", "--baseline", default=BIN_BASELINE, help="Path to baseline binary")
    parser.add_argument("-t", "--tunable", default=BIN_TUNABLE, help="Path to overrides-enabled tunable binary")
    parser.add_argument("-s", "--size", type=int, choices=[7, 8, 9], default=None, help="Specific size to evaluate. Defaults to all.")
    parser.add_argument("-w", "--winners", default=None, help="Path to SPSA winners text file to load env overrides from.")
    parser.add_argument("-l", "--log", default=None, help="Optional path to write comparison tables to a log file.")
    parser.add_argument("--no-use-stdin", action="store_true", help="Disable stdin mode batching for comparisons.")
    parser.add_argument('--max-workers', type=int, default=4)
    parser.add_argument('--repeats', type=int, default=2, help='Even number of balanced AB/BA rounds')
    parser.add_argument('--warmup', type=int, default=1, help='Unmeasured instances per worker and round')
    parser.add_argument('--timeout', type=float, default=15.0)
    parser.add_argument('--records', default=None, help='Per-instance JSONL output path')
    args = parser.parse_args()
    if args.max_workers < 1 or args.repeats < 2 or args.repeats % 2 or args.warmup < 0 or args.timeout <= 0:
        parser.error('workers/timeout must be positive, repeats positive and even, warmup nonnegative')
    
    # Auto-resolve winners file path if not provided but size is specified
    winners_file = args.winners
    if winners_file is None and args.size is not None:
        possible_winners = os.path.join(ROOT_DIR, "scratch", f"spsa_winners_s{args.size}.txt")
        if os.path.exists(possible_winners):
            winners_file = possible_winners
    
    tuned_env = None
    if winners_file:
        print(f"Loading tuned parameters from: {winners_file}")
        tuned_env = load_tuned_env(winners_file)
        
    validation_tasks = []
    
    # 1. Size 7
    if args.size is None or args.size == 7:
        s7_clues = read_clues(PATH_S7)
        if s7_clues:
            validation_tasks.append(("Size 7 Complete Set (Single Solution)", "-s 1", s7_clues))
            validation_tasks.append(("Size 7 Complete Set (Full Enumeration)", "-s 0", s7_clues))
            
    # 2. Size 8
    if args.size is None or args.size == 8:
        s8_easy = read_clues(PATH_S8_EASY)
        s8_med = read_clues(PATH_S8_MED)
        s8_hard = read_clues(PATH_S8_HARD)
        s8_xhard = read_clues(PATH_S8_XHARD)
        
        s8_all = s8_easy + s8_med + s8_hard + s8_xhard
        s8_easy_med = s8_easy + s8_med
        
        if s8_all:
            validation_tasks.append(("Size 8 Complete Set (Single Solution)", "-s 1", s8_all))
        if s8_easy_med:
            validation_tasks.append(("Size 8 Easy/Medium Complete Set (Full Enumeration)", "-s 0", s8_easy_med))
            
    # 3. Size 9
    if args.size is None or args.size == 9:
        s9_calib = read_clues(PATH_S9)
        s9_harder = read_clues(PATH_S9_HARDER)
        
        if s9_calib:
            validation_tasks.append(("Size 9 Calibrated Complete Set (Single Solution)", "-s 1", s9_calib))
        if s9_harder:
            validation_tasks.append(("Size 9 Harder Calibrated Complete Set (Single Solution)", "-s 1", s9_harder))
            
    if not validation_tasks:
        print("Error: No validation sets loaded.", file=sys.stderr)
        sys.exit(1)
        
    reports = run_comparison(
        validation_tasks, args.baseline, args.tunable, tuned_env,
        log_path=args.log, use_stdin=not args.no_use_stdin,
        max_workers=args.max_workers, repeats=args.repeats, warmup=args.warmup,
        timeout=args.timeout, size=args.size, records_path=args.records)
    if any(not report['valid'] for report in reports):
        sys.exit(1)

if __name__ == "__main__":
    main()
