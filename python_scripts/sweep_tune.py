#!/usr/bin/env python3
"""One randomized coordinate-sweep pass on fixed SPSA training panels."""
import argparse
import json
import math
import os
from pathlib import Path
import random
from types import SimpleNamespace

import spsa_tune as spsa
from compare_performance import default_environment
from comparison_statistics import validate_policy
from param_metadata import (PARAM_METADATA, PARAM_CONSTRAINTS, PARAMETER_ALIASES,
                            MATH_PARAM_GROUPS, STRATEGY_PARAM_NAMES,
                            STRATEGY_PARAM_GROUPS)
from tuning_objective import (WORK, TIME_NODES, DEFAULT_OBJECTIVE,
                              SWEEP_MODE_WEIGHTS, MODE_WEIGHTS as WORK_MODE_WEIGHTS,
                              SWEEP_TIME_WEIGHTS, REFERENCES,
                              mode_losses, sweep_score)
from spsa_run_metadata import build_run_metadata, clue_identity, save_run_metadata
from symmetry import get_symmetries_from_clue_str

ROOT = Path(__file__).resolve().parent.parent
PARAMETERS = {row[0]: row for row in PARAM_METADATA}
MULTIPLIERS = (-4, -2, -1, -0.5, 0, 0.5, 1, 2, 4)
TIME_WEIGHTS = SWEEP_TIME_WEIGHTS
MODE_WEIGHTS = SWEEP_MODE_WEIGHTS  # public sweep weighting


SWEEP_MODES = ('math7', 'math8', 'math9', 'strategy', *STRATEGY_PARAM_GROUPS)


def active_parameters(mode):
    if mode in ('math7', 'math8', 'math9'):
        names = MATH_PARAM_GROUPS[mode[-1]]
    elif mode == 'strategy':
        names = STRATEGY_PARAM_NAMES | MATH_PARAM_GROUPS['all']
    else:
        names = STRATEGY_PARAM_GROUPS[mode]
    return sorted(n for n in names if PARAMETERS[n][2] > PARAMETERS[n][1])


def mode_sizes(mode):
    return [int(mode[-1])] if mode.startswith('math') else [8, 9]


def affected_sizes(name, sizes):
    for suffix, size in (('_LE7', 7), ('_S8', 8), ('_S9', 9)):
        if name.endswith(suffix):
            return [s for s in sizes if s == size]
    return list(sizes)


def default_values():
    values = {name: kind(default) for name, _, _, default, kind, _ in PARAM_METADATA}
    if any(values[a] > values[b] + eps for a, b, eps in PARAM_CONSTRAINTS):
        raise ValueError('Initial defaults violate parameter constraints')
    return values


def candidate_values(name, values, perturb):
    """Clip only this coordinate; never project a frozen paired coordinate."""
    _, low, high, _, kind, scale = PARAMETERS[name]
    width = (high - low) * scale * perturb
    for left, right, eps in PARAM_CONSTRAINTS:
        if name == left:
            high = min(high, values[right] + eps)
        if name == right:
            low = max(low, values[left] - eps)
    if kind is int:
        low, high = math.ceil(low), math.floor(high)
    candidates = {values[name]: [0]}
    for multiplier in MULTIPLIERS:
        if multiplier == 0:
            continue
        value = kind(round(values[name] + multiplier * width)) if kind is int else values[name] + multiplier * width
        value = min(high, max(low, value))
        candidates.setdefault(value, []).append(multiplier)
    return candidates


def sample_panels(datasets, sizes, counts, rng):
    panels = {}
    for size in sizes:
        for enum in ([False, True] if size in (7, 8) else [False]):
            count = counts[(size, enum)]
            bank = datasets[f's{size}_train']
            if len(bank) < count:
                raise ValueError(f'Size {size} training bank has {len(bank)} clues; need {count}')
            indices = rng.sample(range(len(bank)), count)
            clues = [rng.choice(get_symmetries_from_clue_str(bank[i])) for i in indices]
            key = f's{size}_{"enumeration" if enum else "single"}'
            panels[key] = dict(size=size, enumeration=enum, indices=indices, clues=clues,
                               identity=clue_identity(clues))
    return panels


def environment(values):
    env = default_environment()
    env.update({n: str(v) for n, v in values.items()})
    for old, name in PARAMETER_ALIASES.items():
        env[old] = env[name]
    return env


class PanelObjective:
    def __init__(self, panels, workers, use_stdin, objective=TIME_NODES):
        self.panels = panels
        self.workers = workers
        self.use_stdin = use_stdin
        self.objective = objective

    def __call__(self, values, sizes):
        env = environment(values)
        results = {size: dict(time=0.0, nodes=0.0) for size in sizes}
        for panel in self.panels.values():
            size, enum = panel['size'], panel['enumeration']
            if size not in results:
                continue
            tasks = [('-s 0' if enum else '-s 1', clue) for clue in panel['clues']]
            times, nodes = spsa.evaluate_subset(env, tasks, self.workers, self.use_stdin)
            if len(times) != len(tasks) or len(nodes) != len(tasks):
                raise RuntimeError('Incomplete training evaluation')
            weight = (WORK_MODE_WEIGHTS if self.objective == WORK
                      else MODE_WEIGHTS)[size][int(enum)]
            time_loss, node_loss, _, _ = mode_losses(size, enum, times, nodes)
            results[size]['time'] += weight * time_loss
            results[size]['nodes'] += weight * node_loss
        for size, result in results.items():
            result['score'] = sweep_score(
                size, result['time'], result['nodes'], self.objective)
            if not all(math.isfinite(x) for x in result.values()):
                raise RuntimeError('Nonfinite training objective')
        return results


def combined_score(results):
    return sum(r['score'] for r in results.values()) / len(results)


def coordinate_sweep(initial, names, sizes, evaluate, rng, perturb,
                     log=print, checkpoint=lambda *_: None):
    values = dict(initial)
    order = list(names)
    rng.shuffle(order)
    results = evaluate(values, sizes)
    initial_results = {s: dict(r) for s, r in results.items()}
    history = []
    checkpoint(values, results, history, order, initial_results)
    for index, name in enumerate(order, 1):
        start = values[name]
        best_value, best_results = start, results
        best_score = combined_score(results)
        grid = candidate_values(name, values, perturb)
        candidates = [v for v in grid if v != start]
        rng.shuffle(candidates)
        trials = [dict(value=start, multipliers=grid[start], results=results,
                       score=best_score, cached=True)]
        log(f'Parameter {index}/{len(order)}: {name}; start={start:.15g}; score={best_score:.10g}')
        for value in candidates:
            candidate = dict(values, **{name: value})
            candidate_results = dict(results)
            candidate_results.update(evaluate(candidate, affected_sizes(name, sizes)))
            score = combined_score(candidate_results)
            trials.append(dict(value=value, multipliers=grid[value], results=candidate_results,
                               score=score, cached=False))
            log(f'  candidate={value:.15g} multipliers={grid[value]} score={score:.10g} losses={candidate_results}')
            if score < best_score - 1e-12:
                best_value, best_results, best_score = value, candidate_results, score
        values[name] = best_value
        results = best_results
        history.append(dict(parameter=name, start=start, selected=best_value, trials=trials))
        log(f'  selected={best_value:.15g}; change={best_value - start:+.10g}; score={best_score:.10g}')
        checkpoint(values, results, history, order, initial_results)
    return values, results, history


def output_path(mode):
    folder = ROOT / 'scratch'
    folder.mkdir(exist_ok=True)
    index = 0
    while True:
        path = folder / f'sweep_winners_{mode}_{index}.txt'
        if not path.exists() and not path.with_suffix('.json').exists():
            return path
        index += 1


def save_checkpoint(path, values, names, metadata, label):
    text = f'SWEEP WINNING PARAMETERS ({metadata["mode"]}; {label})\n'
    text += ''.join(f'#define {n} {values[n]:.17g}\n' for n in sorted(names))
    temporary = path.with_suffix('.txt.tmp')
    temporary.write_text(text)
    temporary.replace(path)
    save_run_metadata(path, metadata, label)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=SWEEP_MODES, required=True)
    parser.add_argument('--nodes-time', action='store_const', dest='objective',
                        const=TIME_NODES, help='Tune with measured wall time + search nodes instead of calibrated work')
    parser.set_defaults(objective=DEFAULT_OBJECTIVE)
    parser.add_argument('--work-model', type=Path, default=spsa.DEFAULT_MODEL,
                        help='Pooled v2 work model used by default')
    parser.add_argument('--no-compare', action='store_true')
    parser.add_argument('--seed', type=int)
    parser.add_argument('--log', help='Progress log; defaults beside the unique winner file')
    parser.add_argument('--max-workers', type=int, default=4)
    parser.add_argument('--no-stdin', dest='stdin', action='store_false', default=True)
    parser.add_argument('--perturb', type=float, default=0.03,
                        help='Normal perturbation fraction; grid uses 0, ±0.5, ±1, ±2, ±4 widths')
    parser.add_argument('--s7-single', type=int, default=2048, help='le7 single-solution panel size (math7 only)')
    parser.add_argument('--s7-enumeration', type=int, default=512, help='le7 enumeration panel size (math7 only)')
    parser.add_argument('--s8-single', type=int, default=1024)
    parser.add_argument('--s8-enumeration', type=int, default=64)
    parser.add_argument('--s9-single', type=int, default=2084)
    parser.add_argument('--comparison-repeats', type=int, default=2)
    parser.add_argument('--comparison-warmup', type=int, default=1)
    parser.add_argument('--comparison-timeout', type=float, default=10.0)
    parser.add_argument('--comparison-timeout-penalty', type=float, default=4.0)
    parser.add_argument('--comparison-win-tolerance', type=float, default=0.10)
    args = parser.parse_args(argv)
    if min(args.max_workers, args.s7_single, args.s7_enumeration,
           args.s8_single, args.s8_enumeration, args.s9_single) < 1:
        parser.error('Workers and panel sizes must be positive')
    if not math.isfinite(args.perturb) or args.perturb <= 0:
        parser.error('Perturbation fraction must be finite and positive')
    try:
        validate_policy(args.comparison_timeout, args.comparison_timeout_penalty,
                        args.comparison_win_tolerance)
    except ValueError as error:
        parser.error(str(error))
    if args.comparison_repeats < 2 or args.comparison_repeats % 2 or args.comparison_warmup < 0:
        parser.error('Comparison repeats must be positive and even; warmup nonnegative')
    if args.seed is None:
        args.seed = random.SystemRandom().getrandbits(64)
    return args


def _main_impl(argv=None):
    args = parse_args(argv)
    spsa.configure_objective(args)
    sizes = mode_sizes(args.mode)
    workers = min(args.max_workers, os.cpu_count() or 1)
    rng = random.Random(args.seed)
    names = active_parameters(args.mode)
    values = default_values()
    datasets = {}
    for size in sizes:
        datasets.update(spsa.load_datasets(size))
        if not datasets[f's{size}_val'] and not args.no_compare:
            raise ValueError(f'Missing size {size} validation dataset')
    counts = {(7, False): args.s7_single, (7, True): args.s7_enumeration,
              (8, False): args.s8_single, (8, True): args.s8_enumeration,
              (9, False): args.s9_single}
    panels = sample_panels(datasets, sizes, counts, rng)
    path = output_path(args.mode)
    if args.log is None:
        args.log = str(path.with_suffix('.log'))
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_args = SimpleNamespace(
        **{name: str(value) if isinstance(value, Path) else value
           for name, value in vars(args).items()},
        size=sizes[0], tune_mode=args.mode, batch_size=None)
    metadata = build_run_metadata(metadata_args, datasets, PARAM_METADATA, names, workers, values)
    metadata.update(optimizer='coordinate_sweep', mode=args.mode,
                    size=sizes[0] if len(sizes) == 1 else None, sizes=sizes,
                    batch_size=None, panels=panels, multipliers=MULTIPLIERS,
                    objective=dict(kind=args.objective, work_model_sha256=spsa.WORK_MODEL_SHA256,
                                    time_weights=TIME_WEIGHTS, size_weights={s: 1/len(sizes) for s in sizes},
                                   s8_mode_weights=dict(single=0.5, enumeration=1.5),
                                   mode_weights={s: dict(single=MODE_WEIGHTS[s][0],
                                                        enumeration=MODE_WEIGHTS[s][1]) for s in sizes}),
                    comparison_status='skipped' if args.no_compare else 'pending')
    objective = PanelObjective(panels, workers, args.stdin, args.objective)
    with log_path.open('w') as handle:
        def log(message):
            print(message, flush=True)
            print(message, file=handle, flush=True)

        def checkpoint(current, results, history, order, initial_results):
            metadata.update(results=results, history=history, parameter_order=order,
                            initial_results=initial_results, final_parameters=current)
            save_checkpoint(path, current, names, metadata, f'Coordinate {len(history)}/{len(order)}')

        log(f'Sweep seed: {args.seed}; mode: {args.mode}; parameters: {len(names)}')
        log(f'Sweep winners: {path}; log: {log_path}')
        log(f'Fixed panels: { {k: p["identity"] for k, p in panels.items()} }')
        save_checkpoint(path, values, names, metadata, 'Started')
        final, results, history = coordinate_sweep(values, names, sizes, objective, rng,
                                                  args.perturb, log, checkpoint)
        save_checkpoint(path, final, names, metadata, 'Final')
        log(f'Sweep complete: score={combined_score(results):.10g}; winners={path}')
    if not args.no_compare:
        theta = [(final[n] - low) / (high - low) if high > low else 0.0
                 for n, low, high, *_ in PARAM_METADATA]
        try:
            for size in sizes:
                comparison_args = SimpleNamespace(**vars(args), size=size, enumeration_only=False)
                if len(sizes) > 1:
                    comparison_args.log = str(log_path.with_name(f'{log_path.stem}_s{size}{log_path.suffix}'))
                spsa.run_post_tuning_comparison(comparison_args, datasets, theta)
        except Exception:
            metadata['comparison_status'] = 'failed'
            save_checkpoint(path, final, names, metadata, 'Final')
            raise
        metadata['comparison_status'] = 'complete'
        save_checkpoint(path, final, names, metadata, 'Final')



def main(argv=None):
    try:
        return _main_impl(argv)
    finally:
        spsa.configure_objective(SimpleNamespace(objective=TIME_NODES))


if __name__ == '__main__':
    main()
