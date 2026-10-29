"""Build node-balanced SPSA datasets without modifying active datasets."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import threading

from param_metadata import PARAM_METADATA
from .common import (BANDS, ROOT, Cache, atomic_json, digest, key, read_clues,
                     sha256, timestamp, workspace_lock)
from .difficulty import anchors, band_for, distribution, matched_split, quotas, score
from .measurement import screen


def input_inventory(root, sizes):
    datasets = root / 'puzzle_bank/spsa_datasets'
    originals = [datasets / f'size{size}_{split}.txt'
                 for size in sizes for split in ('train', 'val')]
    for path in originals:
        if not path.is_file():
            raise ValueError(f'Missing original dataset: {path}')
    exclusions = sorted(set(datasets.rglob('*.txt')) | set((root / 'benchmark_sets').rglob('*.txt')))
    return originals, {path.relative_to(root).as_posix(): sha256(path) for path in exclusions}


def excluded_keys(root, paths, sizes):
    result = {size: set() for size in sizes}
    from .common import normalize
    for relative in paths:
        path = root / relative
        if path.name.startswith('_'):
            continue  # solution-count files, not clue sets
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                clue = normalize(line)
            except ValueError:
                continue
            size = len(clue.split()) // 4
            if size in result:
                result[size].add(key(clue))
    return result


def identify(args, root):
    originals, inputs = input_inventory(root, args.sizes)
    settings = {name: getattr(args, name) for name in (
        'sizes', 'train_count', 'validation_count', 'difficulty_mix', 'seed',
        'max_workers', 'timeout', 'recheck_threshold', 'reference_count',
        'candidate_batch_size', 'burn_in', 'gap')}
    sources = {}
    for pattern in ('python_scripts/dataset_generation/*.py', 'python_scripts/symmetry.py',
                    'python_scripts/comparison_measurements.py', 'python_scripts/param_metadata.py'):
        for path in sorted(root.glob(pattern)):
            sources[path.relative_to(root).as_posix()] = sha256(path)
    identity = {'schema_version': 1, 'settings': settings,
                'solver_sha256': sha256(args.solver), 'inputs': inputs,
                'sources': sources, 'python': sys.version,
                'dependencies': {name: importlib.metadata.version(name) for name in ('numpy', 'numba')}}
    return identity, originals


def build_size(size, args, root, binary, cache, excluded, env, stopped, progress):
    from .generator import generate_unique_instances
    settings = vars(args)
    validation_quotas = quotas(args.train_count, args.validation_count, args.difficulty_mix)
    rng = random.Random(args.seed + size)
    raw_reference = [clue for split in ('train', 'val') for clue in
                     read_clues(root / f'puzzle_bank/spsa_datasets/size{size}_{split}.txt', size)]
    reference = list({key(clue): clue for clue in raw_reference}.values())
    reference = rng.sample(reference, min(args.reference_count, len(reference)))
    workers = args.max_workers

    def evaluate(clues):
        pool = ThreadPoolExecutor(max_workers=workers)
        try:
            # Bounded waves avoid queuing an entire expensive dataset at once.
            for start in range(0, len(clues), workers):
                wave = clues[start:start + workers]
                futures = [pool.submit(screen, clue, size, binary, env, settings, cache, stopped)
                           for clue in wave]
                for future in futures:
                    row = future.result()
                    progress['puzzles_screened'] += 1
                    progress['outcomes'][row['reason']] += 1
                    yield row
                atomic_json(Path(args.work_dir) / 'progress.json', progress)
                print(f"Size {size}: screened {progress['puzzles_screened']} puzzles; "
                      f"outcomes={dict(progress['outcomes'])}", flush=True)
        finally:
            if sys.exc_info()[0] is not None:
                stopped.set()
            pool.shutdown(wait=True, cancel_futures=True)

    reference_key = f'references_{size}'
    references = cache.get(reference_key)
    if references is None:
        references = list(evaluate(reference))
        cache.put(reference_key, references)
    eligible_reference = [row for row in references if row['accepted']]
    reference_anchors = anchors(eligible_reference, size)
    selected = {band: [] for band in BANDS}
    seen = set(excluded)
    rejection_counts = Counter()
    for batch in range(args.max_batches):
        batch_key = f'candidates_{size}_{batch}'
        clues = cache.get(batch_key)
        if clues is None:
            batch_seed = args.seed + size * 1_000_000 + batch
            clues = generate_unique_instances(size, args.candidate_batch_size,
                                               args.burn_in, args.gap, seed=batch_seed,
                                               excluded_keys=[tuple(map(int, item.split())) for item in seen])
            cache.put(batch_key, clues)
        fresh = [clue for clue in clues if key(clue) not in seen]
        seen.update(key(clue) for clue in fresh)
        for row in evaluate(fresh):
            rejection_counts[row['reason']] += 1
            if row['accepted']:
                value = score(row, reference_anchors, size)
                band = band_for(value, reference_anchors)
                if len(selected[band]) < validation_quotas[band] * 11:
                    selected[band].append(dict(row, score=value, band=band))
        print(f"Size {size}: batch {batch + 1}; quotas " + ', '.join(
            f'{band} {len(selected[band])}/{validation_quotas[band] * 11}' for band in BANDS), flush=True)
        if all(len(selected[band]) == validation_quotas[band] * 11 for band in BANDS):
            break
    else:
        raise ValueError(f'Size {size}: --max-batches reached before quotas filled; '
                         'cached work preserved, no partial dataset activated')
    train, validation = matched_split(selected, validation_quotas, args.seed + size)
    report = {'anchors': reference_anchors, 'reference_requested': len(reference),
              'reference_accepted': len(eligible_reference), 'outcomes': dict(rejection_counts),
              'reference': distribution(eligible_reference, size),
              'train': distribution(train, size), 'validation': distribution(validation, size)}
    return train, validation, report


def run(args, root=ROOT):
    args.solver = Path(args.solver).resolve()
    args.work_dir = str(Path(args.work_dir).resolve())
    work = Path(args.work_dir)
    identity, originals = identify(args, root)
    with workspace_lock(work):
        cache = Cache(work / 'cache.sqlite', identity)
        stopped = threading.Event()
        try:
            binary = work / 'baseline_solver'
            if not binary.exists():
                shutil.copy2(args.solver, binary)
            if sha256(binary) != identity['solver_sha256']:
                raise ValueError('Frozen solver checksum mismatch')
            env = os.environ.copy()
            for name, *_ in PARAM_METADATA:
                env.pop(name, None)
            version = cache.get('version')
            if version is None:
                version = timestamp() + '-' + digest(identity)[:8]
                cache.put('version', version)
            excluded = excluded_keys(root, identity['inputs'], args.sizes)
            payload = work / 'results'
            payload.mkdir(exist_ok=True)
            progress = {'puzzles_screened': 0, 'outcomes': Counter()}
            rows, reports = {}, {}
            for size in args.sizes:
                train, validation, report = build_size(
                    size, args, root, binary, cache, excluded[size], env, stopped, progress)
                rows[str(size)] = {'train': train, 'val': validation}
                reports[str(size)] = report
            # Refuse to package an inconsistent snapshot if inputs changed mid-run.
            if any(sha256(root / name) != value for name, value in identity['inputs'].items()):
                raise ValueError('Input files changed during generation')
            for size, splits in rows.items():
                for split, instances in splits.items():
                    target = payload / f'spsa_datasets/size{size}_{split}.txt'
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(''.join(f'"{row["clue"]}"\n' for row in instances))
            old_checksums = {}
            for old in originals:
                relative = f'spsa_datasets/old_versions/{version}/{old.name}'
                target = payload / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old, target)
                old_checksums[old.name] = sha256(old)
            atomic_json(payload / 'instances.json', rows)
            cache.export(payload / 'measurements.jsonl')
            with (payload / 'excluded_keys.jsonl').open('w') as output:
                for size in args.sizes:
                    for canonical in sorted(excluded[size]):
                        output.write(json.dumps({'size': size, 'key': canonical}) + '\n')
            try:
                revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root,
                                                   stderr=subprocess.DEVNULL, text=True).strip()
            except (OSError, subprocess.CalledProcessError):
                revision = None
            report_lines = ['# SPSA dataset generation report', '',
                            f'Version: {version}', '',
                            'Active datasets were not changed. Timings are baseline measurements '
                            'on this machine; perturbed configurations can take longer.', '',
                            '| Size / split | Count | Single p50 / p99 (s) | Enumeration p50 / p99 (s) |',
                            '|---|---:|---:|---:|']
            for size, report in reports.items():
                for split in ('reference', 'train', 'validation'):
                    stats = report[split]
                    single = stats['single_seconds']
                    enum = stats.get('enumeration_seconds')
                    enum_text = f"{enum['p50']:.5g} / {enum['p99']:.5g}" if enum else 'n/a'
                    report_lines.append(f"| {size} / {split} | {stats['count']} | "
                                        f"{single['p50']:.5g} / {single['p99']:.5g} | {enum_text} |")
                train = report['train']
                solver_work = (16 * (train['single_seconds']['mean'] +
                                    train['enumeration_seconds']['mean']) if size == '8' else
                               256 * train['single_seconds']['mean'])
                report['estimated_baseline_iteration_seconds'] = 3 * solver_work / args.max_workers
                report_lines.extend(['', f"Size {size}: estimated baseline iteration time with current "
                                     f"tuner batch size and {args.max_workers} workers: "
                                     f"{report['estimated_baseline_iteration_seconds']:.3g}s "
                                     '(three evaluations; excludes overhead).', ''])
            atomic_json(payload / 'report.json', reports)
            (payload / 'report.md').write_text('\n'.join(report_lines))
            atomic_json(payload / 'progress.json', progress)
            manifest = dict(identity, version=version, revision=revision,
                            execution_max_batches=args.max_batches,
                            platform=platform.platform(), originals=old_checksums,
                            files={path.relative_to(payload).as_posix(): sha256(path)
                                   for path in sorted(payload.rglob('*'))
                                   if path.is_file() and path.name != 'manifest.json'})
            atomic_json(payload / 'manifest.json', manifest)
            from .artifacts import package, verify_directory
            verify_directory(payload)
            bundle = package(payload, work / f'spsa_datasets_{version}.tar.gz')
            print(f'Completed. Active datasets are unchanged.\nBundle: {bundle}\n'
                  f'SHA256: {sha256(bundle)}', flush=True)
            return bundle
        except (KeyboardInterrupt, InterruptedError):
            stopped.set()
            print('Interrupted; cached measurements preserved. Re-run the same command to resume.', flush=True)
            raise
        finally:
            cache.close()
