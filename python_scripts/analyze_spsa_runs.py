#!/usr/bin/env python3
"""Analyze size/mode/configuration cohorts using each run's starting values."""
import argparse
import ast
import glob
import hashlib
import json
import math
import os
import re
import statistics
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from param_metadata import PARAM_METADATA, get_active_param_names

DEFAULTS = {p[0]: p[3] for p in PARAM_METADATA}


def parse_run_file(filepath):
    size, mode, values = None, 'unknown', {}
    with open(filepath) as source:
        for line in source:
            header = re.search(r'SIZE\s+(\d+)', line, re.I)
            if header and size is None:
                size = int(header[1])
            declared_mode = re.search(r'\bmode=(all|strategy|math)\b', line)
            if declared_mode:
                mode = declared_mode[1]
            elif 'strategy' in line.lower():
                mode = 'strategy'
            elif 'math' in line.lower():
                mode = 'math'
            match = re.match(r'^\s*(?:#define\s+)?([A-Z0-9_]+)\s*[:=]?\s*([0-9.eE+-]+)\s*$', line)
            if match:
                value = float(match[2])
                if not math.isfinite(value):
                    raise ValueError(f'{filepath}: non-finite parameter {match[1]}')
                values[match[1]] = value
    return size, mode, values


def load_run_metadata(filepath):
    sidecar = os.path.splitext(filepath)[0] + '.json'
    if os.path.exists(sidecar):
        with open(sidecar) as source:
            metadata = json.load(source)
        return metadata, 'run metadata'
    # Historical downloads may include a static defaults snapshot. Never execute it.
    snapshot = os.path.join(os.path.dirname(filepath), 'param_metadata.py')
    if os.path.exists(snapshot):
        with open(snapshot) as source:
            tree = ast.parse(source.read())
        for statement in tree.body:
            if isinstance(statement, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id == 'PARAM_METADATA'
                    for target in statement.targets):
                defaults = {ast.literal_eval(row.elts[0]): ast.literal_eval(row.elts[3])
                            for row in statement.value.elts}
                metadata = {'defaults': defaults}
                manifest = os.path.join(os.path.dirname(filepath), 'manifest.json')
                if os.path.exists(manifest):
                    with open(manifest) as source:
                        command = json.load(source).get('command', '')
                    mode = re.search(r'--tune-mode\s+(all|strategy|math)\b', command)
                    if mode:
                        metadata['tune_mode'] = mode[1]
                return metadata, 'historical defaults snapshot'
    return {}, 'current defaults fallback (historical baseline unverified)'


def cohort_key(size, mode, metadata, provenance):
    # Seeds differ by design. Changes to defaults, data or optimizer settings must
    # not silently become another sample in the same statistical population.
    config_keys = ('iterations', 'lr', 'alpha', 'perturb', 'gamma', 'batch_size',
                   'grad_clip', 'mom_clip', 'beta', 'stdin', 'enumeration_only')
    config = metadata.get('config', {})
    identity = {
        'defaults': metadata.get('defaults', DEFAULTS),
        'initial_parameters': metadata.get('initial_parameters'),
        'active_parameters': metadata.get('active_parameters'),
        'datasets': metadata.get('datasets'),
        'source_sha256': metadata.get('source_sha256'),
        'workers': metadata.get('workers'),
        'batch_size': metadata.get('batch_size'),
        'config': {key: config.get(key) for key in config_keys},
        'provenance': provenance,
    }
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:12]
    return size, mode, digest


def parameter_statistics(values, baseline):
    n = len(values)
    median = statistics.median(values)
    mean = statistics.mean(values)
    std = statistics.pstdev(values)
    tolerance = max(1e-12, abs(baseline) * 1e-12)
    shift = median - baseline
    up = sum(value > baseline + tolerance for value in values)
    down = sum(value < baseline - tolerance for value in values)
    ratio = 0.0 if abs(shift) <= tolerance else (abs(shift) / std if std else math.inf)
    if n < 2:
        signal = 'INSUFFICIENT RUNS'
    elif ratio >= 2.0:
        signal = 'STRONG SIGNAL'
    elif ratio >= 1.0:
        signal = 'MODERATE SIGNAL'
    else:
        signal = 'FLAT / NOISE'
    return {'n': n, 'baseline': baseline, 'median': median, 'mean': mean,
            'std': std, 'shift_pct': shift / abs(baseline) * 100 if baseline else None,
            's_ratio': ratio, 'up': up, 'down': down, 'ties': n - up - down,
            'signal': signal}


def analyze_files(files, size_filter=None):
    cohorts = {}
    for filepath in files:
        size, mode, values = parse_run_file(filepath)
        metadata, provenance = load_run_metadata(filepath)
        if metadata.get('size', size) != size:
            raise ValueError(f'{filepath}: header size disagrees with metadata')
        mode = metadata.get('tune_mode', mode)
        if size_filter is not None and size != size_filter:
            continue
        if size not in (7, 8, 9):
            print(f'Warning: skipping {filepath}: no supported size in header', file=sys.stderr)
            continue
        if metadata.get('complete') is False:
            print(f'Warning: skipping incomplete run {filepath}', file=sys.stderr)
            continue
        key = cohort_key(size, mode, metadata, provenance)
        cohorts.setdefault(key, []).append((filepath, values, metadata, provenance))
    reports = []
    for (size, mode, identity), runs in sorted(cohorts.items()):
        all_keys = set().union(*(values.keys() for _, values, _, _ in runs))
        keys = [key for key in sorted(all_keys)
                if not (size != 7 and key.endswith('_LE7'))
                and not any(key.endswith(f'_S{other}') for other in (7, 8, 9) if other != size)]
        active = runs[0][2].get('active_parameters')
        if active is None and mode in ('math', 'strategy', 'all'):
            active = get_active_param_names(mode, size)
        if active is not None:
            keys = [key for key in keys if key in active]
        baseline = runs[0][2].get('initial_parameters') or runs[0][2].get('defaults', DEFAULTS)
        parameters = {}
        for key in keys:
            if key not in baseline:
                print(f'Warning: skipping {key}: no starting value', file=sys.stderr)
                continue
            vals = [values[key] for _, values, _, _ in runs if key in values]
            parameters[key] = parameter_statistics(vals, baseline[key])
        reports.append({'size': size, 'mode': mode, 'cohort': identity,
                        'runs': len(runs), 'files': [row[0] for row in runs],
                        'baseline_source': runs[0][3], 'parameters': parameters})
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='*', help='Winner text files or glob patterns')
    parser.add_argument('--size', type=int, choices=[7, 8, 9])
    parser.add_argument('--json', dest='json_path', help='Optional machine-readable analysis')
    args = parser.parse_args()
    patterns = args.files or [os.path.join(ROOT_DIR, 'scratch', 'run_*.txt')]
    files = sorted({os.path.abspath(path) for pattern in patterns for path in glob.glob(pattern)})
    if not files:
        parser.error('No run files found')
    reports = analyze_files(files, args.size)
    print(f'Found {len(files)} unique winner files; {len(reports)} compatible cohorts.')
    for report in reports:
        print(f"\nSIZE {report['size']} | MODE {report['mode']} | "
              f"{report['runs']} RUNS | COHORT {report['cohort']}")
        print(f"Baseline: {report['baseline_source']}")
        print(f"{'PARAMETER':42} | {'N':>3} | {'START':>12} | {'MEDIAN':>12} | "
              f"{'STD':>10} | {'SHIFT %':>9} | {'UP/DOWN/TIE':>12} | {'S_RATIO':>7} | SIGNAL")
        for name, row in report['parameters'].items():
            shift = f"{row['shift_pct']:+.4f}" if row['shift_pct'] is not None else 'n/a'
            agreement = f"{row['up']}/{row['down']}/{row['ties']}"
            print(f"{name:42} | {row['n']:3} | {row['baseline']:12.8g} | "
                  f"{row['median']:12.8g} | {row['std']:10.4g} | {shift:>9} | "
                  f"{agreement:>12} | {row['s_ratio']:7.2f} | {row['signal']}")
    if args.json_path:
        # JSON has no infinity literal; preserve an exact zero-spread signal as text.
        serializable = [dict(report, parameters={
            key: dict(row, s_ratio=row['s_ratio'] if math.isfinite(row['s_ratio']) else 'inf')
            for key, row in report['parameters'].items()}) for report in reports]
        os.makedirs(os.path.dirname(os.path.abspath(args.json_path)), exist_ok=True)
        with open(args.json_path, 'w') as output:
            json.dump(serializable, output, indent=2, allow_nan=False)
            output.write('\n')


if __name__ == '__main__':
    main()
