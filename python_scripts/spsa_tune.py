#!/usr/bin/env python3
import subprocess
import time
import concurrent.futures
import os
import sys
import random
import math
import argparse
import select
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# Add SCRIPT_DIR to sys.path to allow importing compare_performance
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from symmetry import get_random_symmetry, canonize_clue_str as canonize
from param_metadata import PARAM_METADATA, PARAM_CONSTRAINTS, get_active_param_names
from spsa_metrics import get_sgm_shifts, shifted_geo_mean, mean_log_shifted
from tuning_objective import (WORK, TIME_NODES, DEFAULT_OBJECTIVE, MODE_WEIGHTS,
                              mode_losses, spsa_components)
from tuning_work_runtime import load_model, parse_record, DEFAULT_MODEL
from comparison_measurements import unrestricted_environment, search_status
from spsa_run_metadata import build_run_metadata, save_run_metadata

# Training timeout scoring matches the default post-tuning PAR-4 policy.
TRAINING_TIMEOUT = 10.0
TRAINING_TIMEOUT_PENALTY = 4.0
TRAINING_TIMEOUT_SECONDS = TRAINING_TIMEOUT * TRAINING_TIMEOUT_PENALTY
WORK_WATCHDOG_SECONDS = 60.0

# Globals
LOG_FILE_HANDLE = None
RUN_METADATA = None


def resolve_binary_path(path):
    if not path:
        return path
    if os.name == 'nt' or sys.platform.startswith('win'):
        if not path.lower().endswith('.exe'):
            if os.path.exists(path + '.exe'):
                return path + '.exe'
    return path


BIN_CURR = resolve_binary_path(os.path.join(ROOT_DIR, "skyscraper_solver"))
BIN_NATIVE = BIN_CURR
ACTIVE_OBJECTIVE = TIME_NODES  # direct Python callers default to time + nodes
WORK_MODEL = None
WORK_MODEL_SHA256 = None


def configure_objective(args):
    """Select the tuner binary and validate its calibration before tuning."""
    global BIN_CURR, ACTIVE_OBJECTIVE, WORK_MODEL, WORK_MODEL_SHA256, WORK_WATCHDOG_SECONDS
    WORK_WATCHDOG_SECONDS = getattr(args, "work_watchdog", 60.0)
    ACTIVE_OBJECTIVE = getattr(args, "objective", TIME_NODES)
    if ACTIVE_OBJECTIVE == WORK:
        WORK_MODEL, WORK_MODEL_SHA256 = load_model(
            getattr(args, "work_model", DEFAULT_MODEL))
        BIN_CURR = resolve_binary_path(os.path.join(ROOT_DIR, "skyscraper_solver_work"))
    elif ACTIVE_OBJECTIVE == TIME_NODES:
        WORK_MODEL = WORK_MODEL_SHA256 = None
        BIN_CURR = BIN_NATIVE
    else:
        raise ValueError("Unknown tuning objective")


BIN_BASELINE = resolve_binary_path(os.path.join(ROOT_DIR, "skyscraper_solver_main"))

SPSA_DATASET_DIR = Path(ROOT_DIR) / 'puzzle_bank' / 'spsa_datasets'


def project_constraints(theta):
    name_to_idx = {name: idx for idx, (name, *_) in enumerate(PARAM_METADATA)}
    theta_projected = list(theta)

    # Run projection loop to resolve boundary clamping conflicts
    for _ in range(5):
        changed = False
        for min_name, max_name, eps in PARAM_CONSTRAINTS:
            if min_name not in name_to_idx or max_name not in name_to_idx:
                continue
            i = name_to_idx[min_name]
            j = name_to_idx[max_name]

            _, pmin_i, pmax_i, _, _, _ = PARAM_METADATA[i]
            _, pmin_j, pmax_j, _, _, _ = PARAM_METADATA[j]

            range_i = pmax_i - pmin_i
            range_j = pmax_j - pmin_j
            x = pmin_i + theta_projected[i] * range_i
            y = pmin_j + theta_projected[j] * range_j

            if x > y + eps:
                diff = x - y - eps
                x_new = x - diff / 2.0
                y_new = y + diff / 2.0

                theta_projected[i] = max(0.0, min(1.0, (x_new - pmin_i) / range_i)) if range_i > 0 else 0.0
                theta_projected[j] = max(0.0, min(1.0, (y_new - pmin_j) / range_j)) if range_j > 0 else 0.0
                changed = True
        if not changed:
            break
    return theta_projected


def log_print(*args, **kwargs):
    print(*args, **kwargs)
    if LOG_FILE_HANDLE:
        print(*args, **kwargs, file=LOG_FILE_HANDLE)
        LOG_FILE_HANDLE.flush()



def get_deterministic_split(clues, train_ratio):
    """
    Groups clues by symmetry, sorts them deterministically by canonized key,
    and splits into train and validation sets.
    """
    groups = {}
    for clue in clues:
        key = canonize(clue)
        if key not in groups:
            groups[key] = []
        groups[key].append(clue)

    sorted_keys = sorted(groups.keys())
    split_idx = int(len(sorted_keys) * train_ratio)

    train_keys = sorted_keys[:split_idx]
    val_keys = sorted_keys[split_idx:]

    train_clues = []
    for k in train_keys:
        train_clues.extend(groups[k])

    val_clues = []
    for k in val_keys:
        val_clues.extend(groups[k])

    return train_clues, val_clues


def read_clues(file_path):
    if not os.path.exists(file_path):
        print(f"Error: file not found at {file_path}", file=sys.stderr)
        return []
    with open(file_path, "r") as f:
        return [line.strip().strip('"') for line in f if line.strip()]


def run_solver_instance(env, opt, clue, timeout=None):
    if timeout is None:
        timeout = WORK_WATCHDOG_SECONDS if WORK_MODEL is not None else TRAINING_TIMEOUT
    env = unrestricted_environment(env)
    t_start = time.perf_counter()
    try:
        proc = subprocess.Popen(
            [BIN_CURR] + opt.split() + [clue],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                stdout, stderr = proc.communicate(timeout=0.5)
            except Exception:
                stdout = ""
            if WORK_MODEL is not None:
                raise RuntimeError(f"Work tuning watchdog expired after {timeout:g}s; "
                                   "no wall-clock penalty was scored. "
                                   "Increase --work-watchdog or reduce worker load.")
            return float(timeout) * TRAINING_TIMEOUT_PENALTY, 100000

        elapsed = time.perf_counter() - t_start
        if proc.returncode != 0:
            if WORK_MODEL is not None:
                raise RuntimeError(f"Instrumented solver failed: {stderr[:200]}")
            return float(timeout) * TRAINING_TIMEOUT_PENALTY, 100000

        lines = stdout.splitlines()
        status = search_status(lines)
        if status == 'timeout':
            # Solver-reported incomplete searches use a fixed policy, not the watchdog.
            return TRAINING_TIMEOUT_SECONDS, 100000
        if status == 'error':
            raise ValueError('Malformed solver search status')
        if WORK_MODEL is not None:
            predicted, measured_nodes, _ = parse_record(lines, WORK_MODEL)
            return predicted, measured_nodes

        nodes = 100000
        for line in stdout.splitlines():
            if line.startswith("Nodes visited:"):
                nodes = int(line.split(":")[1].strip())
                break
        return elapsed, nodes
    except Exception:
        if WORK_MODEL is not None:
            raise
        return float(timeout) * TRAINING_TIMEOUT_PENALTY, 100000


def read_with_timeout(proc, timeout=TRAINING_TIMEOUT):
    lines = []
    t_start = time.perf_counter()
    while True:
        elapsed = time.perf_counter() - t_start
        rem = timeout - elapsed
        if rem <= 0:
            return None
        try:
            r, _, _ = select.select([proc.stdout], [], [], rem)
            if not r:
                return None
            line_bytes = proc.stdout.readline()
            if not line_bytes:
                return None
            line = line_bytes.decode('utf-8')
            lines.append(line)
            if line.strip() == "--- END_OF_INSTANCE ---":
                break
        except Exception:
            return None
    return lines


def evaluate_subset_standalone(env, tasks, max_workers):
    times = []
    nodes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_solver_instance, env, opt, clue) for opt, clue in tasks]
        for fut in futures:
            t, n = fut.result()
            times.append(t)
            nodes.append(n)
    return times, nodes


def _run_opt_group_stdin(env, opt, clues_with_indices):
    env = unrestricted_environment(env)
    proc = subprocess.Popen(
        [BIN_CURR] + opt.split() + ["--stdin"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        bufsize=0,
        env=env
    )

    group_results = []
    try:
        for idx, clue in clues_with_indices:
            t0 = time.perf_counter()
            proc.stdin.write((f'"{clue}"\n').encode('utf-8'))
            proc.stdin.flush()

            timeout = WORK_WATCHDOG_SECONDS if WORK_MODEL is not None else TRAINING_TIMEOUT
            lines = read_with_timeout(proc, timeout=timeout)
            elapsed = time.perf_counter() - t0

            if lines is None:
                if WORK_MODEL is not None:
                    raise RuntimeError(f'Work tuning watchdog/stream failure after a limit of {timeout:g}s; '
                                       'no wall-clock penalty was scored. '
                                       'Increase --work-watchdog or reduce worker load.')
                try:
                    proc.kill()
                except Exception:
                    pass
                proc.wait()
                proc = subprocess.Popen(
                    [BIN_CURR] + opt.split() + ["--stdin"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    bufsize=0,
                    env=env
                )
                group_results.append((idx, TRAINING_TIMEOUT_SECONDS, 100000))
                continue

            status = search_status(lines)
            if status == 'timeout' or (status == 'error' and WORK_MODEL is None):
                group_results.append((idx, TRAINING_TIMEOUT_SECONDS, 100000))
                continue
            if status == 'error':
                raise ValueError('Malformed solver search status')
            if WORK_MODEL is not None:
                predicted, node_count, _ = parse_record(lines, WORK_MODEL)
                elapsed = predicted
            else:
                node_count = 100000
                for line in lines:
                    if line.startswith("Nodes visited:"):
                        node_count = int(line.split(":")[1].strip())
                        break
            group_results.append((idx, elapsed, node_count))
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.kill()
        except Exception:
            pass
        proc.wait()
    return group_results


def evaluate_subset_stdin(env, tasks, max_workers):
    tasks_with_indices = [(i, opt, clue) for i, (opt, clue) in enumerate(tasks)]

    by_opt_indexed = {}
    for i, opt, clue in tasks_with_indices:
        if opt not in by_opt_indexed:
            by_opt_indexed[opt] = []
        by_opt_indexed[opt].append((i, clue))

    times = [0.0] * len(tasks)
    nodes = [0] * len(tasks)

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for opt, clues in by_opt_indexed.items():
            subgroups = [[] for _ in range(max_workers)]
            for idx, item in enumerate(clues):
                subgroups[idx % max_workers].append(item)
            subgroups = [sg for sg in subgroups if sg]

            for sg in subgroups:
                futures.append(executor.submit(_run_opt_group_stdin, env, opt, sg))

        for fut in futures:
            for idx, elapsed, node_count in fut.result():
                times[idx] = elapsed
                nodes[idx] = node_count

    return times, nodes


def evaluate_subset(env, tasks, max_workers, use_stdin=False):
    if not use_stdin:
        return evaluate_subset_standalone(env, tasks, max_workers)
    return evaluate_subset_stdin(env, tasks, max_workers)


def get_env_for_theta(theta):
    env = unrestricted_environment()
    for val, (name, pmin, pmax, default, ptype, scale) in zip(theta, PARAM_METADATA):
        phys_val = pmin + val * (pmax - pmin)
        if ptype is int:
            phys_val = int(round(phys_val))
        env[name] = str(phys_val)
    return env


def get_physical_params(theta):
    phys = {}
    for val, (name, pmin, pmax, default, ptype, scale) in zip(theta, PARAM_METADATA):
        phys_val = pmin + val * (pmax - pmin)
        if ptype is int:
            phys_val = int(round(phys_val))
        phys[name] = phys_val
    return phys


def get_default_theta():
    theta = []
    for name, pmin, pmax, default, ptype, scale in PARAM_METADATA:
        val = (default - pmin) / (pmax - pmin) if pmax > pmin else 0.0
        theta.append(val)
    return theta


# --- Dataset Loaders ---

def load_datasets_size_7():
    s7_train = read_clues(SPSA_DATASET_DIR / "le7_train.txt")
    s7_val = read_clues(SPSA_DATASET_DIR / "le7_val.txt")
    log_print(f"Loaded le7 dataset: {len(s7_train)} train clues, {len(s7_val)} validation clues.")
    return {"s7_train": s7_train, "s7_val": s7_val}


def load_datasets_size_8():
    s8_train = read_clues(SPSA_DATASET_DIR / "size8_train.txt")
    s8_val = read_clues(SPSA_DATASET_DIR / "size8_val.txt")
    log_print(f"Loaded Size 8 datasets: {len(s8_train)} train clues, {len(s8_val)} validation clues.")
    return {"s8_train": s8_train, "s8_val": s8_val}


def load_datasets_size_9():
    s9_train = read_clues(SPSA_DATASET_DIR / "size9_train.txt")
    s9_val = read_clues(SPSA_DATASET_DIR / "size9_val.txt")
    log_print(f"Loaded Size 9 datasets: {len(s9_train)} train clues, {len(s9_val)} validation clues.")
    return {"s9_train": s9_train, "s9_val": s9_val}


def load_datasets(size):
    if size == 7:
        return load_datasets_size_7()
    elif size == 8:
        return load_datasets_size_8()
    elif size == 9:
        return load_datasets_size_9()
    return {}


# --- Loss Evaluators (shared numerical policy in tuning_objective.py) ---

def _mode_tasks(bank, count, enumeration):
    selected = random.sample(bank, min(len(bank), count))
    option = "-s 0" if enumeration else "-s 1"
    return [(option, get_random_symmetry(clue)) for clue in selected]


def _evaluate_mode(env, tasks, size, enumeration, max_workers, use_stdin):
    times, nodes = evaluate_subset(env, tasks, max_workers, use_stdin)
    return mode_losses(size, enumeration, times, nodes)


def make_loss_evaluator_s7(datasets, batch_size, max_workers, use_stdin,
                           enumeration_only, objective=TIME_NODES):
    bank = datasets["s7_train"]
    enum_tasks = _mode_tasks(bank, batch_size, True)
    single_tasks = None if enumeration_only else _mode_tasks(bank, batch_size, False)

    def get_loss(config_theta):
        env = get_env_for_theta(config_theta)
        if single_tasks is not None:
            ts, ns, sgm_ts, sgm_ns = _evaluate_mode(
                env, single_tasks, 7, False, max_workers, use_stdin)
        te, ne, sgm_te, sgm_ne = _evaluate_mode(
            env, enum_tasks, 7, True, max_workers, use_stdin)
        if single_tasks is None:
            return (*spsa_components(te, ne, objective),
                    (sgm_te, sgm_ne, sgm_te, sgm_ne))
        weights = MODE_WEIGHTS[7]
        time_loss = weights[0] * ts + weights[1] * te
        nodes_loss = weights[0] * ns + weights[1] * ne
        return (*spsa_components(time_loss, nodes_loss, objective),
                (sgm_ts, sgm_ns, sgm_te, sgm_ne))

    return get_loss


def make_loss_evaluator_s8(datasets, batch_size, max_workers, use_stdin,
                           enumeration_only, objective=TIME_NODES):
    bank = datasets["s8_train"]
    count = batch_size if enumeration_only else max(1, batch_size // 2)
    enum_tasks = _mode_tasks(bank, count, True)
    single_tasks = None if enumeration_only else _mode_tasks(bank, count, False)

    def get_loss(config_theta):
        env = get_env_for_theta(config_theta)
        if single_tasks is not None:
            ts, ns, sgm_ts, sgm_ns = _evaluate_mode(
                env, single_tasks, 8, False, max_workers, use_stdin)
        te, ne, sgm_te, sgm_ne = _evaluate_mode(
            env, enum_tasks, 8, True, max_workers, use_stdin)
        if single_tasks is None:
            return (*spsa_components(te, ne, objective),
                    (sgm_te, sgm_ne, sgm_te, sgm_ne))
        weights = MODE_WEIGHTS[8]
        time_loss = weights[0] * ts + weights[1] * te
        nodes_loss = weights[0] * ns + weights[1] * ne
        return (*spsa_components(time_loss, nodes_loss, objective),
                (sgm_ts, sgm_ns, sgm_te, sgm_ne))

    return get_loss


def make_loss_evaluator_s9(datasets, batch_size, max_workers, use_stdin,
                           enumeration_only, objective=TIME_NODES):
    bank = datasets["s9_train"]
    tasks = _mode_tasks(bank, batch_size, enumeration_only)

    def get_loss(config_theta):
        env = get_env_for_theta(config_theta)
        time_loss, nodes_loss, sgm_time, sgm_nodes = _evaluate_mode(
            env, tasks, 9, enumeration_only, max_workers, use_stdin)
        return (*spsa_components(time_loss, nodes_loss, objective),
                (sgm_time, sgm_nodes, sgm_time, sgm_nodes))

    return get_loss


def build_loss_evaluator(size, datasets, batch_size, max_workers, use_stdin,
                         enumeration_only, objective=TIME_NODES):
    factories = {7: make_loss_evaluator_s7, 8: make_loss_evaluator_s8,
                 9: make_loss_evaluator_s9}
    if size not in factories:
        raise ValueError(f"Unsupported size: {size}")
    return factories[size](datasets, batch_size, max_workers, use_stdin,
                           enumeration_only, objective)


# --- Output Helpers ---

def resolve_winners_filename(size):
    os.makedirs(os.path.join(ROOT_DIR, "scratch"), exist_ok=True)
    base_path = f"scratch/spsa_winners_s{size}"
    ext = ".txt"
    idx = 0
    while os.path.exists(os.path.join(ROOT_DIR, f"{base_path}_{idx}{ext}")):
        idx += 1
    return os.path.join(ROOT_DIR, f"{base_path}_{idx}{ext}")


def save_winners(filename, theta_vals, label, size, active_names):
    phys = get_physical_params(theta_vals)
    with open(filename, "w") as f:
        mode = RUN_METADATA['tune_mode'] if RUN_METADATA else 'unknown'
        f.write(f"SPSA WINNING PARAMETERS FOR SIZE {size} ({label}; mode={mode})\n")
        f.write("==============================================\n")
        for name, val in phys.items():
            if name not in active_names:
                continue
            f.write(f"#define {name} {val}\n")
    if RUN_METADATA:
        save_run_metadata(filename, RUN_METADATA, label)


def report_parameter_values(initial_values, final_values, active_names):
    names = [name for name in initial_values if name in active_names]
    width = max([len('Parameter')] + [len(name) for name in names])
    log_print("\nTuned Parameter Values (physical units):")
    log_print(f"{'Parameter':<{width}} | {'Start':>14} | {'End':>14} | {'Abs. Change':>14}")
    log_print('-' * (width + 51))
    for name in names:
        start, end = initial_values[name], final_values[name]
        log_print(f"{name:<{width}} | {start:>14.10g} | {end:>14.10g} | {abs(end - start):>14.10g}")


def log_iteration_status(k, grad_time_norm, grad_nodes_norm, ema_time_norm, ema_nodes_norm):
    normalized_time = grad_time_norm / max(1e-5, ema_time_norm)
    normalized_nodes = grad_nodes_norm / max(1e-5, ema_nodes_norm)
    log_print(f"Iter {k:3d} | "
              f"GradNormClipped(T/N): {grad_time_norm:.4f}/{grad_nodes_norm:.4f} | "
              f"GradEMA(T/N): {ema_time_norm:.4f}/{ema_nodes_norm:.4f} | "
              f"GradNormalized(T/N): {normalized_time:.4f}/{normalized_nodes:.4f}")


def make_perturbation_directions(active_indices, dimensions, count):
    """Randomized orthogonal Hadamard rows, or independent Rademacher fallback."""
    n = len(active_indices)
    if count == 1:
        # Preserve the original RNG draws, including draws for inactive parameters.
        return [[random.choice([-1.0, 1.0]) for _ in range(dimensions)]]
    if n and n & (n - 1) == 0 and count <= n:
        # Sylvester Hadamard matrix: row/column permutations and sign flips
        # preserve exact orthogonality on the active coordinates.
        rows = random.sample(range(n), count)
        columns = random.sample(range(n), n)
        signs = [random.choice([-1.0, 1.0]) for _ in range(n)]
        directions = []
        for row in rows:
            delta = [0.0] * dimensions
            for col, index in enumerate(active_indices):
                parity = (row & columns[col]).bit_count() % 2
                delta[index] = signs[col] * (-1.0 if parity else 1.0)
            directions.append(delta)
        return directions
    active_set = set(active_indices)
    return [[random.choice([-1.0, 1.0]) if i in active_set else 0.0
             for i in range(dimensions)] for _ in range(count)]


def report_sensitivity_analysis(grad_time_sum, grad_nodes_sum, iterations, directions=1,
                                active_names=None, initial_values=None, final_values=None):
    log_print("\nParameter Sensitivity Analysis (Average Absolute Gradient):")
    names = [name for name, *_ in PARAM_METADATA if active_names is None or name in active_names]
    width = max([len('Parameter')] + [len(name) for name in names])
    log_print(f"{'Parameter':<{width}} | {'Time Loss Sens.':>16} | {'Node Loss Sens.':>16} | {'Total Sens.':>12} | {'Abs. Change':>14}")
    log_print('-' * (width + 70))
    sens_data = []
    for i, (name, *_) in enumerate(PARAM_METADATA):
        if active_names is not None and name not in active_names:
            continue
        if directions == 1:
            avg_gt = avg_gn = total_sens = None
        else:
            avg_gt = grad_time_sum[i] / iterations
            avg_gn = grad_nodes_sum[i] / iterations
            total_sens = avg_gt + avg_gn
        change = (abs(final_values[name] - initial_values[name])
                  if initial_values is not None and final_values is not None else None)
        sens_data.append((name, avg_gt, avg_gn, total_sens, change))
    sens_data.sort(key=lambda row: row[3] if row[3] is not None else -1, reverse=True)
    for name, avg_gt, avg_gn, total_sens, change in sens_data:
        sensitivities = ['N/A' if value is None else f'{value:.6f}'
                         for value in (avg_gt, avg_gn, total_sens)]
        change_text = 'N/A' if change is None else f'{change:.10g}'
        log_print(f"{name:<{width}} | {sensitivities[0]:>16} | {sensitivities[1]:>16} | "
                  f"{sensitivities[2]:>12} | {change_text:>14}")


# --- Comparison Runner ---

def run_post_tuning_comparison(args, datasets, theta_final):
    train_tasks = []
    validation_tasks = []

    train_clues = datasets[f"s{args.size}_train"]
    train_subset = train_clues[:len(train_clues) // 10]

    if args.size == 7:
        if not args.enumeration_only:
            train_tasks.append((f"le7 Training Set (Single Solution) ({len(train_subset)} instances)", "-s 1", train_subset))
            validation_tasks.append(("le7 Validation Set (Single Solution)", "-s 1", datasets["s7_val"]))
        train_tasks.append((f"le7 Training Set (Full Enumeration) ({len(train_subset)} instances)", "-s 0", train_subset))
        validation_tasks.append(("le7 Validation Set (Full Enumeration)", "-s 0", datasets["s7_val"]))

    elif args.size == 8:
        if not args.enumeration_only:
            train_tasks.append((f"Size 8 Training Set (Single Solution) ({len(train_subset)} instances)", "-s 1", train_subset))
            validation_tasks.append(("Size 8 Validation Set (Single Solution)", "-s 1", datasets["s8_val"]))
        train_tasks.append((f"Size 8 Training Set (Full Enumeration) ({len(train_subset)} instances)", "-s 0", train_subset))
        validation_tasks.append(("Size 8 Validation Set (Full Enumeration)", "-s 0", datasets["s8_val"]))

    elif args.size == 9:
        mode_flag = "-s 0" if args.enumeration_only else "-s 1"
        mode_lbl = " (Full Enumeration)" if args.enumeration_only else " (Single Solution)"
        train_tasks.append((f"Size 9 Training Set{mode_lbl} ({len(train_subset)} instances)", mode_flag, train_subset))
        validation_tasks.append((f"Size 9 Validation Set{mode_lbl}", mode_flag, datasets["s9_val"]))

    train_log_path = None
    val_log_path = None
    if args.log:
        base, ext = os.path.splitext(args.log)
        train_log_path = f"{base}_train{ext}"
        val_log_path = f"{base}_val{ext}"

    import compare_performance
    train_reports = compare_performance.run_comparison(
        validation_tasks=train_tasks,
        baseline_bin=BIN_NATIVE,
        tunable_bin=BIN_NATIVE,
        tuned_env=get_env_for_theta(theta_final),
        title="TRAINING SET PERFORMANCE COMPARISON (first 10%)",
        log_path=train_log_path,
        use_stdin=args.stdin, max_workers=min(os.cpu_count() or 1, args.max_workers),
        repeats=args.comparison_repeats, warmup=args.comparison_warmup, size=args.size,
        timeout=args.comparison_timeout, timeout_penalty=args.comparison_timeout_penalty,
        win_tolerance=args.comparison_win_tolerance,
        report_work_prediction=getattr(args, 'report_work_prediction', False),
        work_model_path=getattr(args, 'work_model', DEFAULT_MODEL),
        records_path=os.path.splitext(args.log or os.path.join(
            ROOT_DIR, 'scratch', f'spsa_s{args.size}_{args.seed}.log'))[0] + '_train_instances.jsonl'
    )
    val_reports = compare_performance.run_comparison(
        validation_tasks=validation_tasks,
        baseline_bin=BIN_NATIVE,
        tunable_bin=BIN_NATIVE,
        tuned_env=get_env_for_theta(theta_final),
        title="VALIDATION SET PERFORMANCE COMPARISON",
        log_path=val_log_path,
        use_stdin=args.stdin, max_workers=min(os.cpu_count() or 1, args.max_workers),
        repeats=args.comparison_repeats, warmup=args.comparison_warmup, size=args.size,
        timeout=args.comparison_timeout, timeout_penalty=args.comparison_timeout_penalty,
        win_tolerance=args.comparison_win_tolerance,
        report_work_prediction=getattr(args, 'report_work_prediction', False),
        work_model_path=getattr(args, 'work_model', DEFAULT_MODEL),
        records_path=os.path.splitext(args.log or os.path.join(
            ROOT_DIR, 'scratch', f'spsa_s{args.size}_{args.seed}.log'))[0] + '_val_instances.jsonl'
    )

    if any(not report['valid'] for report in train_reports + val_reports):
        raise RuntimeError('Post-tuning comparison invalid; inspect per-instance records')


# --- Core SPSA Loop ---

def run_spsa(args, datasets, max_workers):
    alpha = args.alpha
    gamma = args.gamma
    c = args.perturb
    a = args.lr
    A = 40
    iterations = args.iterations

    if args.batch_size is not None:
        batch_size = args.batch_size
    elif args.size == 9:
        batch_size = 256
    elif args.size == 8:
        batch_size = 32
    else:
        batch_size = 128

    directions = getattr(args, 'directions', 1)
    if directions < 1 or directions > batch_size:
        raise ValueError("directions must be between 1 and the batch size")
    log_print(f"SPSA Batch Size configured: {batch_size}; directions: {directions}")

    theta = project_constraints(get_default_theta())
    initial_values = get_physical_params(theta)
    requested_names = get_active_param_names(args.tune_mode, args.size)
    active_indices = [i for i, (name, pmin, pmax, *_) in enumerate(PARAM_METADATA)
                      if pmax > pmin and name in requested_names]
    active_names = {PARAM_METADATA[i][0] for i in active_indices}
    swa_theta = [0.0] * len(theta)
    swa_count = 0

    grad_time_sum = [0.0] * len(theta)
    grad_nodes_sum = [0.0] * len(theta)

    swa_start = max(1, iterations - 9)

    winners_filename = resolve_winners_filename(args.size)
    log_print(f"SPSA winners file resolved to: {winners_filename}")
    global RUN_METADATA
    RUN_METADATA = build_run_metadata(
        args, datasets, PARAM_METADATA, active_names,
        max_workers, initial_values)
    RUN_METADATA['objective_mode'] = ACTIVE_OBJECTIVE
    RUN_METADATA['work_model_sha256'] = WORK_MODEL_SHA256
    RUN_METADATA['work_model_source'] = (str(getattr(args, 'work_model', DEFAULT_MODEL))
                                          if WORK_MODEL is not None else None)
    RUN_METADATA['sgm_shifts'] = {
        mode: dict(zip(('time', 'nodes'), get_sgm_shifts(args.size, enumeration)))
        for mode, enumeration in [('single', False), ('enumeration', True)]}
    save_run_metadata(winners_filename, RUN_METADATA, 'Started')

    # Modern Optimizer State: Running scale and momentum buffers
    beta = args.beta
    grad_clip_ratio = args.grad_clip
    mom_clip_ratio = args.mom_clip

    mom_time = [0.0] * len(theta)
    mom_nodes = [0.0] * len(theta)

    ema_time_norm = 1.0
    ema_nodes_norm = 1.0
    ema_beta = 0.90

    for k in range(1, iterations + 1):
        ak = a / ((k + A) ** alpha)
        ck = c / (k ** gamma)

        # Partition the existing batch budget across paired perturbation evaluations.
        sizes = [batch_size // directions + (j < batch_size % directions)
                 for j in range(directions)]
        evaluators = [
            build_loss_evaluator(
                size=args.size, datasets=datasets, batch_size=part,
                max_workers=max_workers, use_stdin=args.stdin,
                enumeration_only=args.enumeration_only,
                objective=ACTIVE_OBJECTIVE)
            for part in sizes
        ]
        active_index_set = set(active_indices)
        perturbations = make_perturbation_directions(active_indices, len(theta), directions)

        grad_time = [0.0] * len(theta)
        grad_nodes = [0.0] * len(theta)
        for delta, evaluator, part in zip(perturbations, evaluators, sizes):
            losses = []
            for sign in (1.0, -1.0):
                perturbed = []
                for i, value in enumerate(theta):
                    if i in active_index_set:
                        scale = PARAM_METADATA[i][5]
                        value = max(0.0, min(1.0, value + sign * ck * scale * delta[i]))
                    perturbed.append(value)
                losses.append(evaluator(project_constraints(perturbed)))
            loss_time_plus, loss_nodes_plus, _ = losses[0]
            loss_time_minus, loss_nodes_minus, _ = losses[1]
            # Preserve the existing perturb_scale gradient convention.
            weight = part / batch_size
            for i in active_indices:
                grad_time[i] += weight * (loss_time_plus - loss_time_minus) / (2.0 * ck * delta[i])
                grad_nodes[i] += weight * (loss_nodes_plus - loss_nodes_minus) / (2.0 * ck * delta[i])

        if directions > 1:
            for i in active_indices:
                grad_time_sum[i] += abs(grad_time[i])
                grad_nodes_sum[i] += abs(grad_nodes[i])

        if LOG_FILE_HANDLE:
            LOG_FILE_HANDLE.write(f"Iter {k} grad_time:  {list(grad_time)}\n")
            LOG_FILE_HANDLE.write(f"Iter {k} grad_nodes: {list(grad_nodes)}\n")

        grad_time_norm = math.sqrt(sum(g**2 for g in grad_time))
        grad_nodes_norm = math.sqrt(sum(g**2 for g in grad_nodes))

        # 1. Update running gradient scale
        ema_time_norm = ema_beta * ema_time_norm + (1 - ema_beta) * max(1e-5, grad_time_norm)
        ema_nodes_norm = ema_beta * ema_nodes_norm + (1 - ema_beta) * max(1e-5, grad_nodes_norm)

        # 2. Relative Gradient Norm Clipping (caps outlier batches relative to running scale)
        max_time_norm = grad_clip_ratio * ema_time_norm
        if grad_time_norm > max_time_norm:
            grad_time = [g * (max_time_norm / grad_time_norm) for g in grad_time]
            grad_time_norm = max_time_norm

        max_nodes_norm = grad_clip_ratio * ema_nodes_norm
        if grad_nodes_norm > max_nodes_norm:
            grad_nodes = [g * (max_nodes_norm / grad_nodes_norm) for g in grad_nodes]
            grad_nodes_norm = max_nodes_norm

        # 3. Unit-Normalized Gradients
        grad_time_normed = [g / max(1e-5, ema_time_norm) for g in grad_time]
        grad_nodes_normed = [g / max(1e-5, ema_nodes_norm) for g in grad_nodes]

        # 4. Momentum Buffer Update & Momentum Clipping (protects momentum buffer)
        for i in range(len(theta)):
            mom_time[i] = beta * mom_time[i] + (1.0 - beta) * grad_time_normed[i]
            mom_nodes[i] = beta * mom_nodes[i] + (1.0 - beta) * grad_nodes_normed[i]

        mom_time_norm = math.sqrt(sum(m**2 for m in mom_time))
        if mom_time_norm > mom_clip_ratio:
            mom_time = [m * (mom_clip_ratio / mom_time_norm) for m in mom_time]

        mom_nodes_norm = math.sqrt(sum(m**2 for m in mom_nodes))
        if mom_nodes_norm > mom_clip_ratio:
            mom_nodes = [m * (mom_clip_ratio / mom_nodes_norm) for m in mom_nodes]

        # 5. Parameter Step: strictly controlled by lr (ak)
        # Average step is ~ ak / sqrt(D), maximum step strictly <= ak * mom_clip_ratio
        theta_next = []
        for i in range(len(theta)):
            name, pmin, pmax, _, _, _ = PARAM_METADATA[i]
            is_active = (pmax > pmin) and (name in active_names)
            if is_active:
                v_i = 0.5 * (mom_time[i] + mom_nodes[i])
                step = ak * v_i
                val = max(0.0, min(1.0, theta[i] - step))
            else:
                val = theta[i]
            theta_next.append(val)
        theta = project_constraints(theta_next)

        if k >= swa_start:
            swa_count += 1
            for i in range(len(theta)):
                swa_theta[i] += theta[i]

        log_iteration_status(k, grad_time_norm, grad_nodes_norm, ema_time_norm, ema_nodes_norm)

        if k % 100 == 0:
            if swa_count > 0:
                current_theta = [x / swa_count for x in swa_theta]
                label = f"SWA at Iter {k}"
            else:
                current_theta = list(theta)
                label = f"Iter {k}"
            save_winners(winners_filename, current_theta, label, args.size, active_names)
            log_print(f"Iter {k:3d} | Intermediate SPSA winners written to {winners_filename}")

    log_print("\nSPSA tuning completed!")

    if swa_count > 0:
        theta_final = [x / swa_count for x in swa_theta]
        log_print(f"Computed Stochastic Weight Average (SWA) over the last {swa_count} iterations.")
    else:
        theta_final = list(theta)

    final_values = get_physical_params(theta_final)
    report_parameter_values(initial_values, final_values, active_names)
    report_sensitivity_analysis(grad_time_sum, grad_nodes_sum, iterations, directions,
                                active_names, initial_values, final_values)
    save_winners(winners_filename, theta_final, "Final SWA" if swa_count > 0 else "Final",
                 args.size, active_names)
    log_print(f"\nOptimal generalizing definitions written to {winners_filename}")

    return theta_final


# --- Main CLI Entrypoint ---

def parse_args():
    parser = argparse.ArgumentParser(description="Run SPSA tuning for a solver size group.")
    parser.add_argument("--size", type=int, choices=[7, 8, 9], required=True, help="Solver size group to optimize (7 uses sizes 5–7)")
    parser.add_argument("--nodes-time", action="store_const", const=TIME_NODES,
                        dest="objective", help="Tune with measured wall time + search nodes")
    parser.set_defaults(objective=DEFAULT_OBJECTIVE)
    parser.add_argument("--report-work-prediction", action="store_true",
                        help="Show calibrated work in post-tuning native comparisons")
    parser.add_argument("--work-model", type=Path, default=DEFAULT_MODEL,
                        help="Compact pooled v1 work calibration file")
    parser.add_argument("--work-watchdog", type=float, default=60.0,
                        help="Emergency wall-clock limit per work solve; aborts tuning without scoring (default: 60s)")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of SPSA tuning iterations")
    parser.add_argument("--log", default=None, help="Optional file path to log terminal outputs")
    parser.add_argument("--no-compare", action="store_true", help="Deactivate calling the compare solvers routine at the end of SPSA automatically")
    parser.add_argument("--lr", type=float, default=0.01, help="SPSA initial learning rate step size (a)")
    parser.add_argument("--alpha", type=float, default=0.0, help="SPSA learning rate decay exponent (alpha)")
    parser.add_argument("--perturb", type=float, default=0.03, help="SPSA initial perturbation step size (c)")
    parser.add_argument("--gamma", type=float, default=0.0, help="SPSA perturbation decay exponent (gamma)")
    parser.add_argument("--batch-size", type=int, default=None, help="SPSA batch size (number of sampled instances per iteration)")
    parser.add_argument("--directions", type=int, default=4, help="Perturbation pairs per iteration (1 uses a single direction)")
    parser.add_argument("--grad-clip", type=float, default=2.5, help="Relative gradient norm clipping threshold (multiple of running gradient norm)")
    parser.add_argument("--mom-clip", type=float, default=1.5, help="Momentum buffer norm ceiling factor")
    parser.add_argument("--beta", type=float, default=0.90, help="Momentum decay coefficient (beta)")
    parser.add_argument("--no-stdin", dest="stdin", action="store_false", help="Deactivate using stdin batching to solve puzzles in persistent subprocesses")
    parser.set_defaults(stdin=True)
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum workers to use.")
    parser.add_argument("--tune-mode", choices=["all", "strategy", "math", "effective-depth"], default="all", help="Tune all parameters, shared strategy parameters (including effective depth), size-specific math constants, or only effective-depth coefficients")
    parser.add_argument("--enumeration-only", action="store_true", help="Focus solely on full enumeration benchmarks (-s 0) during tuning")
    parser.add_argument('--seed', type=int, default=None, help='RNG seed; generated and recorded if omitted')
    parser.add_argument('--comparison-repeats', type=int, default=2, help='Even number of AB/BA comparison rounds')
    parser.add_argument('--comparison-warmup', type=int, default=1, help='Unmeasured instances per comparison worker')
    parser.add_argument('--comparison-timeout', type=float, default=10.0, help='Per-instance post-tuning comparison limit in seconds (default: 10)')
    parser.add_argument('--comparison-timeout-penalty', type=float, default=4.0, help='Comparison timeout runtime multiplier (default: 4)')
    parser.add_argument('--comparison-win-tolerance', type=float, default=0.10, help='Comparison timing tie/near-best tolerance (default: 0.10)')
    args = parser.parse_args()
    from comparison_statistics import validate_policy
    try:
        validate_policy(args.comparison_timeout, args.comparison_timeout_penalty, args.comparison_win_tolerance)
    except ValueError as error:
        parser.error(str(error))
    if not math.isfinite(args.work_watchdog) or args.work_watchdog <= 0:
        parser.error("work watchdog must be finite and positive")
    if args.max_workers < 1 or args.iterations < 1 or args.directions < 1 or (args.batch_size is not None and args.batch_size < 1):
        parser.error('workers, iterations and batch size must be positive')
    if args.comparison_repeats < 2 or args.comparison_repeats % 2 or args.comparison_warmup < 0:
        parser.error('comparison repeats must be positive and even; warmup nonnegative')
    return args


def _main_impl():
    args = parse_args()
    if args.seed is None:
        args.seed = random.SystemRandom().getrandbits(64)
    random.seed(args.seed)
    max_workers = min(os.cpu_count() or 1, args.max_workers)

    global LOG_FILE_HANDLE
    if args.log:
        log_dir = os.path.dirname(args.log)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        LOG_FILE_HANDLE = open(args.log, "w")

    log_print(f"SPSA random seed: {args.seed}")
    configure_objective(args)
    log_print(f"Starting SPSA optimization for size {args.size} (iterations: {args.iterations})")
    log_print(f"Training objective: {ACTIVE_OBJECTIVE} (binary={BIN_CURR})")

    datasets = load_datasets(args.size)
    theta_final = run_spsa(args, datasets, max_workers)

    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.close()
        LOG_FILE_HANDLE = None

    if not args.no_compare:
        run_post_tuning_comparison(args, datasets, theta_final)



def main():
    try:
        return _main_impl()
    finally:
        configure_objective(argparse.Namespace(objective=TIME_NODES))


if __name__ == "__main__":
    main()
