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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# Add SCRIPT_DIR to sys.path to allow importing compare_performance
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from symmetry import get_random_symmetry, canonize_clue_str as canonize
from param_metadata import PARAM_METADATA, PARAM_CONSTRAINTS, get_active_param_names

# Globals
LOG_FILE_HANDLE = None


def resolve_binary_path(path):
    if not path:
        return path
    if os.name == 'nt' or sys.platform.startswith('win'):
        if not path.lower().endswith('.exe'):
            if os.path.exists(path + '.exe'):
                return path + '.exe'
    return path


BIN_CURR = resolve_binary_path(os.path.join(ROOT_DIR, "skyscraper_solver"))
BIN_BASELINE = resolve_binary_path(os.path.join(ROOT_DIR, "skyscraper_solver_main"))

# Paths to datasets
PATH_S7 = os.path.join(ROOT_DIR, "puzzle_bank", "puzzle_bank7.txt")

# Size 8 calibrated files
PATH_S8_EASY = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_easy.txt")
PATH_S8_MED = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_medium.txt")
PATH_S8_HARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_hard.txt")
PATH_S8_XHARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_xhard.txt")

# Size 9 calibrated files
PATH_S9_LVL1 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "size9_lvl1.txt")
PATH_S9_LVL2 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "size9_lvl2.txt")
PATH_S9_LVL3 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "size9_lvl3.txt")


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


def run_solver_instance(env, opt, clue, timeout=10.0):
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
            return float(timeout), 100000

        elapsed = time.perf_counter() - t_start
        if proc.returncode != 0:
            return float(timeout), 100000

        nodes = 100000
        for line in stdout.splitlines():
            if line.startswith("Nodes visited:"):
                nodes = int(line.split(":")[1].strip())
                break
        return elapsed, nodes
    except Exception:
        return float(timeout), 100000


def shifted_geo_mean(values, shift):
    if not values:
        return 0.0
    sum_ln = sum(math.log(max(0.0, float(x)) + shift) for x in values)
    return math.exp(sum_ln / len(values)) - shift


def read_with_timeout(proc, timeout=10.0):
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

            lines = read_with_timeout(proc, timeout=10.0)
            elapsed = time.perf_counter() - t0

            if lines is None:
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
                group_results.append((idx, 10.0, 100000))
                continue

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
    env = os.environ.copy()
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
    s7_all = read_clues(PATH_S7)
    split_idx = int(len(s7_all) * 0.9)
    s7_train = s7_all[:split_idx]
    s7_val = s7_all[split_idx:]
    log_print(f"Loaded Size 7 dataset: {len(s7_train)} train clues, {len(s7_val)} validation clues.")
    return {"s7_train": s7_train, "s7_val": s7_val}


def load_datasets_size_8():
    s8_easy = read_clues(PATH_S8_EASY)
    s8_med = read_clues(PATH_S8_MED)
    s8_hard = read_clues(PATH_S8_HARD)
    s8_xhard = read_clues(PATH_S8_XHARD)

    easy_train, easy_val = get_deterministic_split(s8_easy, 0.5)
    med_train, med_val = get_deterministic_split(s8_med, 0.5)
    hard_train, hard_val = get_deterministic_split(s8_hard, 0.5)
    xhard_train, xhard_val = get_deterministic_split(s8_xhard, 0.5)

    datasets = {
        "easy_train": easy_train, "easy_val": easy_val,
        "med_train": med_train, "med_val": med_val,
        "hard_train": hard_train, "hard_val": hard_val,
        "xhard_train": xhard_train, "xhard_val": xhard_val,
        "s8_single_train": easy_train + med_train + hard_train + xhard_train,
        "s8_single_val": easy_val + med_val + hard_val + xhard_val,
        "s8_enum_train": easy_train + med_train,
        "s8_enum_val": easy_val + med_val
    }

    log_print("Loaded Size 8 datasets:")
    log_print(f"  Single train pool: {len(datasets['s8_single_train'])} clues (val: {len(datasets['s8_single_val'])})")
    log_print(f"  Enum train pool:   {len(datasets['s8_enum_train'])} clues (val: {len(datasets['s8_enum_val'])})")
    return datasets


def load_datasets_size_9():
    s9_lvl1 = read_clues(PATH_S9_LVL1)
    s9_lvl2 = read_clues(PATH_S9_LVL2)
    s9_lvl3 = read_clues(PATH_S9_LVL3)

    s9_lvl1_train, s9_lvl1_val = get_deterministic_split(s9_lvl1, 0.9)
    s9_lvl2_train, s9_lvl2_val = get_deterministic_split(s9_lvl2, 0.9)
    s9_lvl3_train, s9_lvl3_val = get_deterministic_split(s9_lvl3, 0.9)

    log_print("Loaded Size 9 datasets:")
    log_print(f"  Lvl 1 train: {len(s9_lvl1_train)} clues (val: {len(s9_lvl1_val)})")
    log_print(f"  Lvl 2 train: {len(s9_lvl2_train)} clues (val: {len(s9_lvl2_val)})")
    log_print(f"  Lvl 3 train: {len(s9_lvl3_train)} clues (val: {len(s9_lvl3_val)})")

    return {
        "s9_lvl1_train": s9_lvl1_train, "s9_lvl1_val": s9_lvl1_val,
        "s9_lvl2_train": s9_lvl2_train, "s9_lvl2_val": s9_lvl2_val,
        "s9_lvl3_train": s9_lvl3_train, "s9_lvl3_val": s9_lvl3_val
    }


def load_datasets(size):
    if size == 7:
        return load_datasets_size_7()
    elif size == 8:
        return load_datasets_size_8()
    elif size == 9:
        return load_datasets_size_9()
    return {}


# --- Loss Evaluators ---

def make_loss_evaluator_s7(datasets, batch_size, max_workers, use_stdin, enumeration_only):
    s7_train = datasets["s7_train"]
    ref_scale_s7_single_time = 0.005
    ref_scale_s7_single_nodes = 350.0
    ref_scale_s7_enum_time = 0.01
    ref_scale_s7_enum_nodes = 2000.0

    if enumeration_only:
        sampled_enum = random.sample(s7_train, min(len(s7_train), batch_size))
        tasks_enum = [("-s 0", get_random_symmetry(clue)) for clue in sampled_enum]

        def get_loss(config_theta):
            env = get_env_for_theta(config_theta)
            t_enum, n_enum = evaluate_subset(env, tasks_enum, max_workers=max_workers, use_stdin=use_stdin)

            sgm_t_e = shifted_geo_mean(t_enum, 0.005)
            sgm_n_e = shifted_geo_mean(n_enum, 1000.0)

            loss_time = 1.0 * (sgm_t_e / ref_scale_s7_enum_time)
            loss_nodes = 1.0 * (sgm_n_e / ref_scale_s7_enum_nodes)

            return loss_time, loss_nodes, (sgm_t_e, sgm_n_e, sgm_t_e, sgm_n_e)
        return get_loss

    sampled_single = random.sample(s7_train, min(len(s7_train), batch_size))
    sampled_enum = random.sample(s7_train, min(len(s7_train), batch_size))
    tasks_single = [("-s 1", get_random_symmetry(clue)) for clue in sampled_single]
    tasks_enum = [("-s 0", get_random_symmetry(clue)) for clue in sampled_enum]

    def get_loss(config_theta):
        env = get_env_for_theta(config_theta)
        t_single, n_single = evaluate_subset(env, tasks_single, max_workers=max_workers, use_stdin=use_stdin)
        t_enum, n_enum = evaluate_subset(env, tasks_enum, max_workers=max_workers, use_stdin=use_stdin)

        sgm_t_s = shifted_geo_mean(t_single, 0.002)
        sgm_n_s = shifted_geo_mean(n_single, 100.0)

        sgm_t_e = shifted_geo_mean(t_enum, 0.005)
        sgm_n_e = shifted_geo_mean(n_enum, 1000.0)

        loss_time = 1.0 * (sgm_t_s / ref_scale_s7_single_time) + 1.5 * (sgm_t_e / ref_scale_s7_enum_time)
        loss_nodes = 1.0 * (sgm_n_s / ref_scale_s7_single_nodes) + 1.5 * (sgm_n_e / ref_scale_s7_enum_nodes)

        return loss_time, loss_nodes, (sgm_t_s, sgm_n_s, sgm_t_e, sgm_n_e)
    return get_loss


def make_loss_evaluator_s8(datasets, batch_size, max_workers, use_stdin, enumeration_only):
    easy_train = datasets["easy_train"]
    med_train = datasets["med_train"]
    hard_train = datasets["hard_train"]
    xhard_train = datasets["xhard_train"]

    ref_scale_s8_single_easy_med_time = 0.02
    ref_scale_s8_single_easy_med_nodes = 3000.0
    ref_scale_s8_single_hard_xhard_time = 0.15
    ref_scale_s8_single_hard_xhard_nodes = 15000.0
    ref_scale_s8_enum_easy_med_time = 0.40
    ref_scale_s8_enum_easy_med_nodes = 50000.0

    if enumeration_only:
        sampled_s8_enum_easy_med = random.sample(easy_train + med_train, min(len(easy_train + med_train), max(1, batch_size // 2)))
        sampled_s8_enum_hard_xhard = random.sample(hard_train + xhard_train, min(len(hard_train + xhard_train), max(1, batch_size // 2)))

        tasks_enum_easy_med = [("-s 0", get_random_symmetry(clue)) for clue in sampled_s8_enum_easy_med]
        tasks_enum_hard_xhard = [("-s 0", get_random_symmetry(clue)) for clue in sampled_s8_enum_hard_xhard]

        def get_loss(config_theta):
            env = get_env_for_theta(config_theta)
            t_e_em, n_e_em = evaluate_subset(env, tasks_enum_easy_med, max_workers=max_workers, use_stdin=use_stdin)
            t_e_hx, n_e_hx = evaluate_subset(env, tasks_enum_hard_xhard, max_workers=max_workers, use_stdin=use_stdin)

            sgm_t_e_em = shifted_geo_mean(t_e_em, 0.200)
            sgm_n_e_em = shifted_geo_mean(n_e_em, 10000.0)

            sgm_t_e_hx = shifted_geo_mean(t_e_hx, 1.000)
            sgm_n_e_hx = shifted_geo_mean(n_e_hx, 50000.0)

            loss_time = 1.0 * (sgm_t_e_em / ref_scale_s8_enum_easy_med_time) + 2.0 * (sgm_t_e_hx / (ref_scale_s8_enum_easy_med_time * 5.0))
            loss_nodes = 1.0 * (sgm_n_e_em / ref_scale_s8_enum_easy_med_nodes) + 2.0 * (sgm_n_e_hx / (ref_scale_s8_enum_easy_med_nodes * 5.0))

            return loss_time, loss_nodes, (sgm_t_e_hx, sgm_n_e_hx, sgm_t_e_em, sgm_n_e_em)
        return get_loss

    sampled_s8_single_easy_med = random.sample(easy_train + med_train, min(len(easy_train + med_train), max(1, batch_size // 4)))
    sampled_s8_single_hard_xhard = random.sample(hard_train + xhard_train, min(len(hard_train + xhard_train), max(1, batch_size // 4)))
    sampled_s8_enum = random.sample(easy_train + med_train, min(len(easy_train + med_train), max(1, batch_size // 2)))

    tasks_single_easy_med = [("-s 1", get_random_symmetry(clue)) for clue in sampled_s8_single_easy_med]
    tasks_single_hard_xhard = [("-s 1", get_random_symmetry(clue)) for clue in sampled_s8_single_hard_xhard]
    tasks_enum = [("-s 0", get_random_symmetry(clue)) for clue in sampled_s8_enum]

    def get_loss(config_theta):
        env = get_env_for_theta(config_theta)
        t_s_em, n_s_em = evaluate_subset(env, tasks_single_easy_med, max_workers=max_workers, use_stdin=use_stdin)
        t_s_hx, n_s_hx = evaluate_subset(env, tasks_single_hard_xhard, max_workers=max_workers, use_stdin=use_stdin)
        t_e_em, n_e_em = evaluate_subset(env, tasks_enum, max_workers=max_workers, use_stdin=use_stdin)

        sgm_t_s_em = shifted_geo_mean(t_s_em, 0.050)
        sgm_n_s_em = shifted_geo_mean(n_s_em, 3000.0)

        sgm_t_s_hx = shifted_geo_mean(t_s_hx, 0.050)
        sgm_n_s_hx = shifted_geo_mean(n_s_hx, 3000.0)

        sgm_t_e_em = shifted_geo_mean(t_e_em, 0.200)
        sgm_n_e_em = shifted_geo_mean(n_e_em, 10000.0)

        loss_time = 0.5 * (sgm_t_s_em / ref_scale_s8_single_easy_med_time) + 1.0 * (sgm_t_s_hx / ref_scale_s8_single_hard_xhard_time) + 2.0 * (sgm_t_e_em / ref_scale_s8_enum_easy_med_time)
        loss_nodes = 0.5 * (sgm_n_s_em / ref_scale_s8_single_easy_med_nodes) + 1.0 * (sgm_n_s_hx / ref_scale_s8_single_hard_xhard_nodes) + 2.0 * (sgm_n_e_em / ref_scale_s8_enum_easy_med_nodes)

        return loss_time, loss_nodes, (sgm_t_s_hx, sgm_n_s_hx, sgm_t_e_em, sgm_n_e_em)
    return get_loss


def make_loss_evaluator_s9(datasets, batch_size, max_workers, use_stdin, enumeration_only):
    s9_lvl1_train = datasets["s9_lvl1_train"]
    s9_lvl2_train = datasets["s9_lvl2_train"]
    s9_lvl3_train = datasets["s9_lvl3_train"]

    ref_scale_s9_lvl1_time = 0.20
    ref_scale_s9_lvl1_nodes = 20000.0
    ref_scale_s9_lvl2_time = 2.00
    ref_scale_s9_lvl2_nodes = 250000.0
    ref_scale_s9_lvl3_time = 15.00
    ref_scale_s9_lvl3_nodes = 1500000.0

    sampled_lvl1 = random.sample(s9_lvl1_train, min(len(s9_lvl1_train), max(1, batch_size // 4)))
    sampled_lvl2 = random.sample(s9_lvl2_train, min(len(s9_lvl2_train), max(1, batch_size // 4)))
    sampled_lvl3 = random.sample(s9_lvl3_train, min(len(s9_lvl3_train), max(1, batch_size // 2)))

    opt_flag = "-s 0" if enumeration_only else "-s 1"
    tasks_lvl1 = [(opt_flag, get_random_symmetry(clue)) for clue in sampled_lvl1]
    tasks_lvl2 = [(opt_flag, get_random_symmetry(clue)) for clue in sampled_lvl2]
    tasks_lvl3 = [(opt_flag, get_random_symmetry(clue)) for clue in sampled_lvl3]

    def get_loss(config_theta):
        env = get_env_for_theta(config_theta)
        t_l1, n_l1 = evaluate_subset(env, tasks_lvl1, max_workers=max_workers, use_stdin=use_stdin)
        t_l2, n_l2 = evaluate_subset(env, tasks_lvl2, max_workers=max_workers, use_stdin=use_stdin)
        t_l3, n_l3 = evaluate_subset(env, tasks_lvl3, max_workers=max_workers, use_stdin=use_stdin)

        sgm_t_l1 = shifted_geo_mean(t_l1, 0.100)
        sgm_n_l1 = shifted_geo_mean(n_l1, 10000.0)

        sgm_t_l2 = shifted_geo_mean(t_l2, 0.500)
        sgm_n_l2 = shifted_geo_mean(n_l2, 50000.0)

        sgm_t_l3 = shifted_geo_mean(t_l3, 1.000)
        sgm_n_l3 = shifted_geo_mean(n_l3, 200000.0)

        loss_time = 0.5 * (sgm_t_l1 / ref_scale_s9_lvl1_time) + 1.5 * (sgm_t_l2 / ref_scale_s9_lvl2_time) + 3.0 * (sgm_t_l3 / ref_scale_s9_lvl3_time)
        loss_nodes = 0.5 * (sgm_n_l1 / ref_scale_s9_lvl1_nodes) + 1.5 * (sgm_n_l2 / ref_scale_s9_lvl2_nodes) + 3.0 * (sgm_n_l3 / ref_scale_s9_lvl3_nodes)

        return loss_time, loss_nodes, (sgm_t_l3, sgm_n_l3, sgm_t_l2, sgm_n_l2)
    return get_loss


def build_loss_evaluator(size, datasets, batch_size, max_workers, use_stdin, enumeration_only):
    if size == 7:
        return make_loss_evaluator_s7(datasets, batch_size, max_workers, use_stdin, enumeration_only)
    elif size == 8:
        return make_loss_evaluator_s8(datasets, batch_size, max_workers, use_stdin, enumeration_only)
    elif size == 9:
        return make_loss_evaluator_s9(datasets, batch_size, max_workers, use_stdin, enumeration_only)
    raise ValueError(f"Unsupported size: {size}")


# --- Output Helpers ---

def resolve_winners_filename(size):
    os.makedirs(os.path.join(ROOT_DIR, "scratch"), exist_ok=True)
    base_path = f"scratch/spsa_winners_s{size}"
    ext = ".txt"
    idx = 0
    while os.path.exists(os.path.join(ROOT_DIR, f"{base_path}_{idx}{ext}")):
        idx += 1
    return os.path.join(ROOT_DIR, f"{base_path}_{idx}{ext}")


def save_winners(filename, theta_vals, label, size):
    phys = get_physical_params(theta_vals)
    with open(filename, "w") as f:
        f.write(f"SPSA WINNING PARAMETERS FOR SIZE {size} ({label})\n")
        f.write("==============================================\n")
        for name, val in phys.items():
            f.write(f"#define {name} {val}\n")


def log_iteration_status(size, k, loss_time, loss_nodes, grad_time_norm, grad_nodes_norm, stats):
    prefix = f"Iter {k:3d} | Loss(T/N): {loss_time:.3f}/{loss_nodes:.3f} | GradNorm(T/N): {grad_time_norm:.4f}/{grad_nodes_norm:.4f} |"
    if size == 7:
        log_print(f"{prefix} S7 Single t: {stats[0]:.4f}s n: {stats[1]:.0f} | S7 Enum t: {stats[2]:.4f}s n: {stats[3]:.0f}")
    elif size == 8:
        log_print(f"{prefix} S8 Hard Single t: {stats[0]:.4f}s n: {stats[1]:.0f} | S8 Enum t: {stats[2]:.4f}s n: {stats[3]:.0f}")
    elif size == 9:
        log_print(f"{prefix} S9 Lvl3 t: {stats[0]:.4f}s n: {stats[1]:.0f} | S9 Lvl2 t: {stats[2]:.4f}s n: {stats[3]:.0f}")


def report_sensitivity_analysis(grad_time_sum, grad_nodes_sum, iterations):
    log_print("\nParameter Sensitivity Analysis (Average Absolute Gradient):")
    log_print("==========================================================")
    log_print(f"{'Parameter Name':<30} | {'Time Loss Sens.':<16} | {'Node Loss Sens.':<16} | {'Total Sens.':<12}")
    log_print("-" * 82)

    sens_data = []
    for i, (name, _, _, _, _, _) in enumerate(PARAM_METADATA):
        avg_gt = abs(grad_time_sum[i]) / iterations
        avg_gn = abs(grad_nodes_sum[i]) / iterations
        total_sens = avg_gt + avg_gn
        sens_data.append((name, avg_gt, avg_gn, total_sens))

    sens_data.sort(key=lambda x: x[3], reverse=True)
    for name, avg_gt, avg_gn, total_sens in sens_data:
        log_print(f"{name:<30} | {avg_gt:<16.6f} | {avg_gn:<16.6f} | {total_sens:<12.6f}")


# --- Comparison Runner ---

def run_post_tuning_comparison(args, datasets, theta_final):
    train_tasks = []
    validation_tasks = []

    if args.size == 7:
        if not args.enumeration_only:
            train_tasks.append(("Size 7 Training Set (Single Solution)", "-s 1", datasets["s7_train"]))
            validation_tasks.append(("Size 7 Validation Set (Single Solution)", "-s 1", datasets["s7_val"]))
        train_tasks.append(("Size 7 Training Set (Full Enumeration)", "-s 0", datasets["s7_train"]))
        validation_tasks.append(("Size 7 Validation Set (Full Enumeration)", "-s 0", datasets["s7_val"]))

    elif args.size == 8:
        if not args.enumeration_only:
            train_tasks.append(("Size 8 Training Set (Single Solution)", "-s 1", datasets["s8_single_train"]))
            validation_tasks.append(("Size 8 Validation Set (Single Solution)", "-s 1", datasets["s8_single_val"]))
        train_tasks.append(("Size 8 Training Set (Full Enumeration)", "-s 0", datasets["s8_enum_train"]))
        validation_tasks.append(("Size 8 Validation Set (Full Enumeration)", "-s 0", datasets["s8_enum_val"]))

    elif args.size == 9:
        mode_flag = "-s 0" if args.enumeration_only else "-s 1"
        mode_lbl = " (Full Enumeration)" if args.enumeration_only else ""
        train_tasks.append((f"Size 9 Level 1 Training Set{mode_lbl}", mode_flag, datasets["s9_lvl1_train"]))
        train_tasks.append((f"Size 9 Level 2 Training Set{mode_lbl}", mode_flag, datasets["s9_lvl2_train"]))
        train_tasks.append((f"Size 9 Level 3 Training Set{mode_lbl}", mode_flag, datasets["s9_lvl3_train"]))
        validation_tasks.append((f"Size 9 Level 1 Validation Set{mode_lbl}", mode_flag, datasets["s9_lvl1_val"]))
        validation_tasks.append((f"Size 9 Level 2 Validation Set{mode_lbl}", mode_flag, datasets["s9_lvl2_val"]))
        validation_tasks.append((f"Size 9 Level 3 Validation Set{mode_lbl}", mode_flag, datasets["s9_lvl3_val"]))

    train_log_path = None
    val_log_path = None
    if args.log:
        base, ext = os.path.splitext(args.log)
        train_log_path = f"{base}_train{ext}"
        val_log_path = f"{base}_val{ext}"

    import compare_performance
    compare_performance.run_comparison(
        validation_tasks=train_tasks,
        baseline_bin=BIN_BASELINE,
        tunable_bin=BIN_CURR,
        tuned_env=get_env_for_theta(theta_final),
        title="TRAINING SET PERFORMANCE COMPARISON",
        log_path=train_log_path
    )
    compare_performance.run_comparison(
        validation_tasks=validation_tasks,
        baseline_bin=BIN_BASELINE,
        tunable_bin=BIN_CURR,
        tuned_env=get_env_for_theta(theta_final),
        title="VALIDATION SET PERFORMANCE COMPARISON",
        log_path=val_log_path
    )


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
    else:
        batch_size = 32

    log_print(f"SPSA Batch Size configured: {batch_size}")

    theta = project_constraints(get_default_theta())
    swa_theta = [0.0] * len(theta)
    swa_count = 0

    grad_time_sum = [0.0] * len(theta)
    grad_nodes_sum = [0.0] * len(theta)

    swa_start = max(1, iterations - 80)

    winners_filename = resolve_winners_filename(args.size)
    log_print(f"SPSA winners file resolved to: {winners_filename}")

    ema_time_norm = 1.0
    ema_nodes_norm = 1.0
    ema_beta = 0.90

    best_loss = float('inf')
    best_theta = list(theta)

    for k in range(1, iterations + 1):
        ak = a / ((k + A) ** alpha)
        ck = c / (k ** gamma)

        get_loss = build_loss_evaluator(
            size=args.size,
            datasets=datasets,
            batch_size=batch_size,
            max_workers=max_workers,
            use_stdin=args.stdin,
            enumeration_only=args.enumeration_only
        )

        active_names = get_active_param_names(args.tune_mode, args.size)
        delta = [random.choice([-1.0, 1.0]) for _ in range(len(theta))]

        # Perturbed plus
        theta_plus_raw = []
        for i in range(len(theta)):
            name, pmin, pmax, _, _, perturb_scale = PARAM_METADATA[i]
            is_active = (pmax > pmin) and (name in active_names)
            if is_active:
                theta_plus_raw.append(max(0.0, min(1.0, theta[i] + ck * perturb_scale * delta[i])))
            else:
                theta_plus_raw.append(theta[i])
        theta_plus = project_constraints(theta_plus_raw)
        loss_time_plus, loss_nodes_plus, _ = get_loss(theta_plus)

        # Perturbed minus
        theta_minus_raw = []
        for i in range(len(theta)):
            name, pmin, pmax, _, _, perturb_scale = PARAM_METADATA[i]
            is_active = (pmax > pmin) and (name in active_names)
            if is_active:
                theta_minus_raw.append(max(0.0, min(1.0, theta[i] - ck * perturb_scale * delta[i])))
            else:
                theta_minus_raw.append(theta[i])
        theta_minus = project_constraints(theta_minus_raw)
        loss_time_minus, loss_nodes_minus, _ = get_loss(theta_minus)

        grad_time = []
        grad_nodes = []
        for i in range(len(theta)):
            name, pmin, pmax, _, _, perturb_scale = PARAM_METADATA[i]
            is_active = (pmax > pmin) and (name in active_names)
            if is_active:
                gt_i = (loss_time_plus - loss_time_minus) / (2.0 * ck * delta[i])
                gn_i = (loss_nodes_plus - loss_nodes_minus) / (2.0 * ck * delta[i])
            else:
                gt_i = 0.0
                gn_i = 0.0
            grad_time.append(gt_i)
            grad_nodes.append(gn_i)
            grad_time_sum[i] += gt_i
            grad_nodes_sum[i] += gn_i

        if LOG_FILE_HANDLE:
            LOG_FILE_HANDLE.write(f"Iter {k} grad_time:  {list(grad_time)}\n")
            LOG_FILE_HANDLE.write(f"Iter {k} grad_nodes: {list(grad_nodes)}\n")

        grad_time_norm = math.sqrt(sum(g**2 for g in grad_time))
        grad_nodes_norm = math.sqrt(sum(g**2 for g in grad_nodes))

        ema_time_norm = ema_beta * ema_time_norm + (1 - ema_beta) * max(1e-5, grad_time_norm)
        ema_nodes_norm = ema_beta * ema_nodes_norm + (1 - ema_beta) * max(1e-5, grad_nodes_norm)

        grad_time_scaled = [g / ema_time_norm for g in grad_time]
        grad_nodes_scaled = [g / ema_nodes_norm for g in grad_nodes]

        max_step = 0.02
        theta_next = []
        for i in range(len(theta)):
            name, pmin, pmax, _, _, _ = PARAM_METADATA[i]
            is_active = (pmax > pmin) and (name in active_names)
            if is_active:
                step_t = ak * grad_time_scaled[i]
                step_n = ak * grad_nodes_scaled[i]
                step_t_c = max(-max_step, min(max_step, step_t))
                step_n_c = max(-max_step, min(max_step, step_n))
                val = max(0.0, min(1.0, theta[i] - step_t_c - step_n_c))
            else:
                val = theta[i]
            theta_next.append(val)
        theta = project_constraints(theta_next)

        if k >= swa_start:
            swa_count += 1
            for i in range(len(theta)):
                swa_theta[i] += theta[i]

        loss_time_curr, loss_nodes_curr, stats = get_loss(theta)
        loss_monitor = loss_time_curr + loss_nodes_curr
        if loss_monitor < best_loss:
            best_loss = loss_monitor
            best_theta = list(theta)

        log_iteration_status(args.size, k, loss_time_curr, loss_nodes_curr, grad_time_norm, grad_nodes_norm, stats)

        if k % 100 == 0:
            if swa_count > 0:
                current_theta = [x / swa_count for x in swa_theta]
                label = f"SWA at Iter {k}"
            else:
                current_theta = list(theta)
                label = f"Iter {k}"
            save_winners(winners_filename, current_theta, label, args.size)
            log_print(f"Iter {k:3d} | Intermediate SPSA winners written to {winners_filename}")

    log_print("\nSPSA tuning completed!")

    if swa_count > 0:
        theta_final = [x / swa_count for x in swa_theta]
        log_print(f"Computed Stochastic Weight Average (SWA) over the last {swa_count} iterations.")
    else:
        theta_final = list(theta)

    phys_best = get_physical_params(theta_final)
    log_print("\nOptimal Parameter Values:")
    log_print("=======================================")
    for name, val in phys_best.items():
        log_print(f"{name} = {val}")

    report_sensitivity_analysis(grad_time_sum, grad_nodes_sum, iterations)

    save_winners(winners_filename, theta_final, "Final SWA" if swa_count > 0 else "Final", args.size)
    log_print(f"\nOptimal generalizing definitions written to {winners_filename}")

    return theta_final


# --- Main CLI Entrypoint ---

def parse_args():
    parser = argparse.ArgumentParser(description="Run SPSA tuning for a specific board size.")
    parser.add_argument("--size", type=int, choices=[7, 8, 9], required=True, help="Solver puzzle size to optimize")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of SPSA tuning iterations")
    parser.add_argument("--log", default=None, help="Optional file path to log terminal outputs")
    parser.add_argument("--no-compare", action="store_true", help="Deactivate calling the compare solvers routine at the end of SPSA automatically")
    parser.add_argument("--lr", type=float, default=0.01, help="SPSA initial learning rate step size (a)")
    parser.add_argument("--alpha", type=float, default=0.0, help="SPSA learning rate decay exponent (alpha)")
    parser.add_argument("--perturb", type=float, default=0.03, help="SPSA initial perturbation step size (c)")
    parser.add_argument("--gamma", type=float, default=0.0, help="SPSA perturbation decay exponent (gamma)")
    parser.add_argument("--batch-size", type=int, default=None, help="SPSA batch size (number of sampled instances per iteration)")
    parser.add_argument("--no-stdin", dest="stdin", action="store_false", help="Deactivate using stdin batching to solve puzzles in persistent subprocesses")
    parser.set_defaults(stdin=True)
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum workers to use.")
    parser.add_argument("--tune-mode", choices=["all", "strategy", "math"], default="all", help="Tuning mode: 'all' (all unfrozen parameters), 'strategy' (tune strategy params only, freeze math constants), 'math' (tune math/scale constants only, freeze strategy params)")
    parser.add_argument("--enumeration-only", action="store_true", help="Focus solely on full enumeration benchmarks (-s 0) during tuning")
    return parser.parse_args()


def main():
    args = parse_args()
    max_workers = min(os.cpu_count() or 1, args.max_workers)

    global LOG_FILE_HANDLE
    if args.log:
        log_dir = os.path.dirname(args.log)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        LOG_FILE_HANDLE = open(args.log, "w")

    log_print(f"Starting SPSA optimization for size {args.size} (iterations: {args.iterations})")

    datasets = load_datasets(args.size)
    theta_final = run_spsa(args, datasets, max_workers)

    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.close()

    if not args.no_compare:
        run_post_tuning_comparison(args, datasets, theta_final)


if __name__ == "__main__":
    main()
