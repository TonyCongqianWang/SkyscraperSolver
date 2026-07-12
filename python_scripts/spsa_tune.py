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
sys.path.append(SCRIPT_DIR)

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

# Parameters Metadata
from param_metadata import PARAM_METADATA, PARAM_CONSTRAINTS

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

            x = pmin_i + theta_projected[i] * (pmax_i - pmin_i)
            y = pmin_j + theta_projected[j] * (pmax_j - pmin_j)

            if x > y + eps:
                diff = x - y - eps
                x_new = x - diff / 2.0
                y_new = y + diff / 2.0

                theta_projected[i] = max(0.0, min(1.0, (x_new - pmin_i) / (pmax_i - pmin_i)))
                theta_projected[j] = max(0.0, min(1.0, (y_new - pmin_j) / (pmax_j - pmin_j)))
                changed = True
        if not changed:
            break
    return theta_projected

LOG_FILE_HANDLE = None

def log_print(*args, **kwargs):
    print(*args, **kwargs)
    if LOG_FILE_HANDLE:
        print(*args, **kwargs, file=LOG_FILE_HANDLE)
        LOG_FILE_HANDLE.flush()

def get_symmetries(T, B, L, R):
    s1 = (T, B, L, R)
    s2 = (L[::-1], R[::-1], B, T)
    s3 = (B[::-1], T[::-1], R[::-1], L[::-1])
    s4 = (R, L, T[::-1], B[::-1])
    s5 = (T[::-1], B[::-1], R, L)
    s6 = (R[::-1], L[::-1], B[::-1], T[::-1])
    s7 = (B, T, L[::-1], R[::-1])
    s8 = (L, R, T, B)
    return [s1, s2, s3, s4, s5, s6, s7, s8]

def canonize(clue_str):
    nums = list(map(int, clue_str.split()))
    n = len(nums) // 4
    T = nums[0:n]
    B = nums[n:2*n]
    L = nums[2*n:3*n]
    R = nums[3*n:4*n]
    symmetries = get_symmetries(T, B, L, R)
    sym_lists = [s[0] + s[1] + s[2] + s[3] for s in symmetries]
    return tuple(min(sym_lists))

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

def evaluate_subset(env, tasks, max_workers, use_stdin=False):
    if not use_stdin:
        times = []
        nodes = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(run_solver_instance, env, opt, clue) for opt, clue in tasks]
            for fut in futures:
                t, n = fut.result()
                times.append(t)
                nodes.append(n)
        return times, nodes

    # Stdin batch mode
    tasks_with_indices = []
    for i, (opt, clue) in enumerate(tasks):
        tasks_with_indices.append((i, opt, clue))

    by_opt_indexed = {}
    for i, opt, clue in tasks_with_indices:
        if opt not in by_opt_indexed:
            by_opt_indexed[opt] = []
        by_opt_indexed[opt].append((i, clue))

    times = [0.0] * len(tasks)
    nodes = [0] * len(tasks)

    def run_opt_group(opt, clues_with_indices):
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
                    # Timeout or process crashed: kill and restart
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

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for opt, clues in by_opt_indexed.items():
            # Partition clues into max_workers subgroups
            subgroups = [[] for _ in range(max_workers)]
            for idx, item in enumerate(clues):
                subgroups[idx % max_workers].append(item)
            subgroups = [sg for sg in subgroups if sg]

            for sg in subgroups:
                futures.append(executor.submit(run_opt_group, opt, sg))

        for fut in futures:
            for idx, elapsed, node_count in fut.result():
                times[idx] = elapsed
                nodes[idx] = node_count

    return times, nodes

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
        val = (default - pmin) / (pmax - pmin)
        theta.append(val)
    return theta

def main():
    parser = argparse.ArgumentParser(description="Run SPSA tuning for a specific board size.")
    parser.add_argument("--size", type=int, choices=[7, 8, 9], required=True, help="Solver puzzle size to optimize")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of SPSA tuning iterations")
    parser.add_argument("--log", default=None, help="Optional file path to log terminal outputs")
    parser.add_argument("--no-compare", action="store_true", help="Deactivate calling the compare solvers routine at the end of SPSA automatically")
    parser.add_argument("--lr", type=float, default=0.002, help="SPSA initial learning rate step size (a)")
    parser.add_argument("--alpha", type=float, default=0.0, help="SPSA learning rate decay exponent (alpha)")
    parser.add_argument("--perturb", type=float, default=0.03, help="SPSA initial perturbation step size (c)")
    parser.add_argument("--gamma", type=float, default=0.0, help="SPSA perturbation decay exponent (gamma)")
    parser.add_argument("--batch-size", type=int, default=None, help="SPSA batch size (number of sampled instances per iteration)")
    parser.add_argument("--stdin", action="store_true", help="Use stdin batching to solve puzzles in persistent subprocesses")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum workers to use.")
    args = parser.parse_args()

    max_workers = min(os.cpu_count() or 1, args.max_workers)

    global LOG_FILE_HANDLE
    if args.log:
        log_dir = os.path.dirname(args.log)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        LOG_FILE_HANDLE = open(args.log, "w")

    log_print(f"Starting SPSA optimization for size {args.size} (iterations: {args.iterations})")

    # 1. Dataset Loading and Splits
    if args.size == 7:
        s7_all = read_clues(PATH_S7)
        split_idx = int(len(s7_all) * 0.9)
        s7_train = s7_all[:split_idx]
        s7_val = s7_all[split_idx:]
        log_print(f"Loaded Size 7 dataset: {len(s7_train)} train clues, {len(s7_val)} validation clues.")

    elif args.size == 8:
        s8_easy = read_clues(PATH_S8_EASY)
        s8_med = read_clues(PATH_S8_MED)
        s8_hard = read_clues(PATH_S8_HARD)
        s8_xhard = read_clues(PATH_S8_XHARD)

        easy_train, easy_val = get_deterministic_split(s8_easy, 0.5)
        med_train, med_val = get_deterministic_split(s8_med, 0.5)
        hard_train, hard_val = get_deterministic_split(s8_hard, 0.5)
        xhard_train, xhard_val = get_deterministic_split(s8_xhard, 0.5)

        s8_single_train = easy_train + med_train + hard_train + xhard_train
        s8_enum_train = easy_train + med_train

        s8_single_val = easy_val + med_val + hard_val + xhard_val
        s8_enum_val = easy_val + med_val

        log_print(f"Loaded Size 8 datasets:")
        log_print(f"  Single train pool: {len(s8_single_train)} clues (val: {len(s8_single_val)})")
        log_print(f"  Enum train pool:   {len(s8_enum_train)} clues (val: {len(s8_enum_val)})")

    elif args.size == 9:
        s9_lvl1 = read_clues(PATH_S9_LVL1)
        s9_lvl2 = read_clues(PATH_S9_LVL2)
        s9_lvl3 = read_clues(PATH_S9_LVL3)

        s9_lvl1_train, s9_lvl1_val = get_deterministic_split(s9_lvl1, 0.9)
        s9_lvl2_train, s9_lvl2_val = get_deterministic_split(s9_lvl2, 0.9)
        s9_lvl3_train, s9_lvl3_val = get_deterministic_split(s9_lvl3, 0.9)

        log_print(f"Loaded Size 9 datasets:")
        log_print(f"  Lvl 1 train: {len(s9_lvl1_train)} clues (val: {len(s9_lvl1_val)})")
        log_print(f"  Lvl 2 train: {len(s9_lvl2_train)} clues (val: {len(s9_lvl2_val)})")
        log_print(f"  Lvl 3 train: {len(s9_lvl3_train)} clues (val: {len(s9_lvl3_val)})")

    # 2. SPSA Hyperparameters
    alpha = args.alpha
    gamma = args.gamma
    c = args.perturb
    a = args.lr
    A = 40
    iterations = args.iterations

    if args.batch_size is not None:
        batch_size = args.batch_size
    else:
        if args.size == 7:
            batch_size = 32
        elif args.size == 8:
            batch_size = 16
        else:
            batch_size = 8

    log_print(f"SPSA Batch Size configured: {batch_size}")

    theta = project_constraints(get_default_theta())
    swa_theta = [0.0] * len(theta)
    swa_count = 0

    # Sensitivity tracking: sum of absolute gradients for each parameter
    grad_time_sum = [0.0] * len(theta)
    grad_nodes_sum = [0.0] * len(theta)

    # Cap SWA iterations to at most 80 iterations to prevent dilution on very long runs
    swa_start = max(1, iterations - 80)

    # Resolve winners filename at the start (always attach a suffix starting with _0)
    os.makedirs(os.path.join(ROOT_DIR, "scratch"), exist_ok=True)
    base_path = f"scratch/spsa_winners_s{args.size}"
    ext = ".txt"
    idx = 0
    while os.path.exists(os.path.join(ROOT_DIR, f"{base_path}_{idx}{ext}")):
        idx += 1
    winners_filename = os.path.join(ROOT_DIR, f"{base_path}_{idx}{ext}")
    log_print(f"SPSA winners file resolved to: {winners_filename}")

    def save_winners(filename, theta_vals, label):
        phys = get_physical_params(theta_vals)
        with open(filename, "w") as f:
            f.write(f"SPSA WINNING PARAMETERS FOR SIZE {args.size} ({label})\n")
            f.write("==============================================\n")
            for name, val in phys.items():
                f.write(f"#define {name} {val}\n")

    # Reference scales
    ref_scale_s7_single_time = 0.005
    ref_scale_s7_single_nodes = 350.0
    ref_scale_s7_enum_time = 0.01
    ref_scale_s7_enum_nodes = 2000.0

    ref_scale_s8_single_easy_med_time = 0.02
    ref_scale_s8_single_easy_med_nodes = 3000.0
    ref_scale_s8_single_hard_xhard_time = 0.15
    ref_scale_s8_single_hard_xhard_nodes = 15000.0
    ref_scale_s8_enum_easy_med_time = 0.40
    ref_scale_s8_enum_easy_med_nodes = 50000.0

    ref_scale_s9_lvl1_time = 0.20
    ref_scale_s9_lvl1_nodes = 20000.0
    ref_scale_s9_lvl2_time = 2.00
    ref_scale_s9_lvl2_nodes = 250000.0
    ref_scale_s9_lvl3_time = 15.00
    ref_scale_s9_lvl3_nodes = 1500000.0

    # Gradient Normalization parameters: Exponential Moving Average of Norms
    ema_time_norm = 1.0
    ema_nodes_norm = 1.0
    ema_beta = 0.90

    best_loss = float('inf')
    best_theta = list(theta)

    for k in range(1, iterations + 1):
        ak = a / ((k + A) ** alpha)
        ck = c / (k ** gamma)

        # Prepare stochastically drawn batches for this step
        if args.size == 7:
            sampled_single = random.sample(s7_train, min(len(s7_train), batch_size))
            sampled_enum = random.sample(s7_train, min(len(s7_train), batch_size))
            tasks_single = [("-s 1", clue) for clue in sampled_single]
            tasks_enum = [("-s 0", clue) for clue in sampled_enum]

            def get_loss(config_theta):
                env = get_env_for_theta(config_theta)
                t_single, n_single = evaluate_subset(env, tasks_single, max_workers=max_workers, use_stdin=args.stdin)
                t_enum, n_enum = evaluate_subset(env, tasks_enum, max_workers=max_workers, use_stdin=args.stdin)

                sgm_t_s = shifted_geo_mean(t_single, 0.002)
                sgm_n_s = shifted_geo_mean(n_single, 100.0)

                sgm_t_e = shifted_geo_mean(t_enum, 0.005)
                sgm_n_e = shifted_geo_mean(n_enum, 1000.0)

                loss_time = 1.0 * (sgm_t_s / ref_scale_s7_single_time) + 1.5 * (sgm_t_e / ref_scale_s7_enum_time)
                loss_nodes = 1.0 * (sgm_n_s / ref_scale_s7_single_nodes) + 1.5 * (sgm_n_e / ref_scale_s7_enum_nodes)

                return loss_time, loss_nodes, (sgm_t_s, sgm_n_s, sgm_t_e, sgm_n_e)

        elif args.size == 8:
            sampled_s8_single_easy_med = random.sample(easy_train + med_train, min(len(easy_train + med_train), max(1, batch_size // 4)))
            sampled_s8_single_hard_xhard = random.sample(hard_train + xhard_train, min(len(hard_train + xhard_train), max(1, batch_size // 4)))
            sampled_s8_enum = random.sample(easy_train + med_train, min(len(easy_train + med_train), max(1, batch_size // 2)))

            tasks_single_easy_med = [("-s 1", clue) for clue in sampled_s8_single_easy_med]
            tasks_single_hard_xhard = [("-s 1", clue) for clue in sampled_s8_single_hard_xhard]
            tasks_enum = [("-s 0", clue) for clue in sampled_s8_enum]

            def get_loss(config_theta):
                env = get_env_for_theta(config_theta)
                t_s_em, n_s_em = evaluate_subset(env, tasks_single_easy_med, max_workers=max_workers, use_stdin=args.stdin)
                t_s_hx, n_s_hx = evaluate_subset(env, tasks_single_hard_xhard, max_workers=max_workers, use_stdin=args.stdin)
                t_e_em, n_e_em = evaluate_subset(env, tasks_enum, max_workers=max_workers, use_stdin=args.stdin)

                sgm_t_s_em = shifted_geo_mean(t_s_em, 0.050)
                sgm_n_s_em = shifted_geo_mean(n_s_em, 3000.0)

                sgm_t_s_hx = shifted_geo_mean(t_s_hx, 0.050)
                sgm_n_s_hx = shifted_geo_mean(n_s_hx, 3000.0)

                sgm_t_e_em = shifted_geo_mean(t_e_em, 0.200)
                sgm_n_e_em = shifted_geo_mean(n_e_em, 10000.0)

                loss_time = 0.5 * (sgm_t_s_em / ref_scale_s8_single_easy_med_time) + 1.0 * (sgm_t_s_hx / ref_scale_s8_single_hard_xhard_time) + 2.0 * (sgm_t_e_em / ref_scale_s8_enum_easy_med_time)
                loss_nodes = 0.5 * (sgm_n_s_em / ref_scale_s8_single_easy_med_nodes) + 1.0 * (sgm_n_s_hx / ref_scale_s8_single_hard_xhard_nodes) + 2.0 * (sgm_n_e_em / ref_scale_s8_enum_easy_med_nodes)

                return loss_time, loss_nodes, (sgm_t_s_hx, sgm_n_s_hx, sgm_t_e_em, sgm_n_e_em)

        elif args.size == 9:
            sampled_lvl1 = random.sample(s9_lvl1_train, min(len(s9_lvl1_train), max(1, batch_size // 4)))
            sampled_lvl2 = random.sample(s9_lvl2_train, min(len(s9_lvl2_train), max(1, batch_size // 4)))
            sampled_lvl3 = random.sample(s9_lvl3_train, min(len(s9_lvl3_train), max(1, batch_size // 2)))

            tasks_lvl1 = [("-s 1", clue) for clue in sampled_lvl1]
            tasks_lvl2 = [("-s 1", clue) for clue in sampled_lvl2]
            tasks_lvl3 = [("-s 1", clue) for clue in sampled_lvl3]

            def get_loss(config_theta):
                env = get_env_for_theta(config_theta)
                t_l1, n_l1 = evaluate_subset(env, tasks_lvl1, max_workers=max_workers, use_stdin=args.stdin)
                t_l2, n_l2 = evaluate_subset(env, tasks_lvl2, max_workers=max_workers, use_stdin=args.stdin)
                t_l3, n_l3 = evaluate_subset(env, tasks_lvl3, max_workers=max_workers, use_stdin=args.stdin)

                sgm_t_l1 = shifted_geo_mean(t_l1, 0.100)
                sgm_n_l1 = shifted_geo_mean(n_l1, 10000.0)

                sgm_t_l2 = shifted_geo_mean(t_l2, 0.500)
                sgm_n_l2 = shifted_geo_mean(n_l2, 50000.0)

                sgm_t_l3 = shifted_geo_mean(t_l3, 1.000)
                sgm_n_l3 = shifted_geo_mean(n_l3, 200000.0)

                loss_time = 0.5 * (sgm_t_l1 / ref_scale_s9_lvl1_time) + 1.5 * (sgm_t_l2 / ref_scale_s9_lvl2_time) + 3.0 * (sgm_t_l3 / ref_scale_s9_lvl3_time)
                loss_nodes = 0.5 * (sgm_n_l1 / ref_scale_s9_lvl1_nodes) + 1.5 * (sgm_n_l2 / ref_scale_s9_lvl2_nodes) + 3.0 * (sgm_n_l3 / ref_scale_s9_lvl3_nodes)

                return loss_time, loss_nodes, (sgm_t_l3, sgm_n_l3, sgm_t_l2, sgm_n_l2)

        delta = [random.choice([-1.0, 1.0]) for _ in range(len(theta))]

        # Perturbed plus
        theta_plus_raw = []
        for i in range(len(theta)):
            perturb_scale = PARAM_METADATA[i][5]
            theta_plus_raw.append(max(0.0, min(1.0, theta[i] + ck * perturb_scale * delta[i])))
        theta_plus = project_constraints(theta_plus_raw)
        loss_time_plus, loss_nodes_plus, _ = get_loss(theta_plus)

        # Perturbed minus
        theta_minus_raw = []
        for i in range(len(theta)):
            perturb_scale = PARAM_METADATA[i][5]
            theta_minus_raw.append(max(0.0, min(1.0, theta[i] - ck * perturb_scale * delta[i])))
        theta_minus = project_constraints(theta_minus_raw)
        loss_time_minus, loss_nodes_minus, _ = get_loss(theta_minus)

        grad_time = []
        grad_nodes = []
        for i in range(len(theta)):
            perturb_scale = PARAM_METADATA[i][5]
            gt_i = (loss_time_plus - loss_time_minus) / (2.0 * ck * perturb_scale * delta[i])
            gn_i = (loss_nodes_plus - loss_nodes_minus) / (2.0 * ck * perturb_scale * delta[i])
            grad_time.append(gt_i)
            grad_nodes.append(gn_i)
            grad_time_sum[i] += gt_i
            grad_nodes_sum[i] += gn_i

        if LOG_FILE_HANDLE:
            LOG_FILE_HANDLE.write(f"Iter {k} grad_time:  {list(grad_time)}\n")
            LOG_FILE_HANDLE.write(f"Iter {k} grad_nodes: {list(grad_nodes)}\n")

        # Compute gradient norms for this iteration
        grad_time_norm = math.sqrt(sum(g**2 for g in grad_time))
        grad_nodes_norm = math.sqrt(sum(g**2 for g in grad_nodes))

        # Update Exponential Moving Average of norms (ensuring no division by zero)
        ema_time_norm = ema_beta * ema_time_norm + (1 - ema_beta) * max(1e-5, grad_time_norm)
        ema_nodes_norm = ema_beta * ema_nodes_norm + (1 - ema_beta) * max(1e-5, grad_nodes_norm)

        # Scale gradients relative to their moving average norms
        grad_time_scaled = [g / ema_time_norm for g in grad_time]
        grad_nodes_scaled = [g / ema_nodes_norm for g in grad_nodes]

        # Parameter updates with step capping applied to scaled gradients
        max_step = 0.02
        theta_next = []
        for i in range(len(theta)):
            step_t = ak * grad_time_scaled[i]
            step_n = ak * grad_nodes_scaled[i]
            step_t_c = max(-max_step, min(max_step, step_t))
            step_n_c = max(-max_step, min(max_step, step_n))
            val = max(0.0, min(1.0, theta[i] - step_t_c - step_n_c))
            theta_next.append(val)
        theta = project_constraints(theta_next)

        # Stochastic Weight Averaging
        if k >= swa_start:
            swa_count += 1
            for i in range(len(theta)):
                swa_theta[i] += theta[i]

        # Monitor
        loss_time_curr, loss_nodes_curr, stats = get_loss(theta)
        loss_monitor = loss_time_curr + loss_nodes_curr
        if loss_monitor < best_loss:
            best_loss = loss_monitor
            best_theta = list(theta)

        if args.size == 7:
            log_print(f"Iter {k:3d} | Loss(T/N): {loss_time_curr:.3f}/{loss_nodes_curr:.3f} | GradNorm(T/N): {grad_time_norm:.4f}/{grad_nodes_norm:.4f} | S7 Single t: {stats[0]:.4f}s n: {stats[1]:.0f} | S7 Enum t: {stats[2]:.4f}s n: {stats[3]:.0f}")
        elif args.size == 8:
            log_print(f"Iter {k:3d} | Loss(T/N): {loss_time_curr:.3f}/{loss_nodes_curr:.3f} | GradNorm(T/N): {grad_time_norm:.4f}/{grad_nodes_norm:.4f} | S8 Hard Single t: {stats[0]:.4f}s n: {stats[1]:.0f} | S8 Enum t: {stats[2]:.4f}s n: {stats[3]:.0f}")
        elif args.size == 9:
            log_print(f"Iter {k:3d} | Loss(T/N): {loss_time_curr:.3f}/{loss_nodes_curr:.3f} | GradNorm(T/N): {grad_time_norm:.4f}/{grad_nodes_norm:.4f} | S9 Lvl3 t: {stats[0]:.4f}s n: {stats[1]:.0f} | S9 Lvl2 t: {stats[2]:.4f}s n: {stats[3]:.0f}")

        # Write intermediate winners every 100 iterations
        if k % 100 == 0:
            if swa_count > 0:
                current_theta = [x / swa_count for x in swa_theta]
                label = f"SWA at Iter {k}"
            else:
                current_theta = list(theta)
                label = f"Iter {k}"
            save_winners(winners_filename, current_theta, label)
            log_print(f"Iter {k:3d} | Intermediate SPSA winners written to {winners_filename}")

    log_print("\nSPSA tuning completed!")

    # Compute final theta using SWA if applicable
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

    # Report Sensitivity Analysis
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

    # Write final winners to resolved file path
    save_winners(winners_filename, theta_final, "Final SWA" if swa_count > 0 else "Final")
    log_print(f"\nOptimal generalizing definitions written to {winners_filename}")

    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.close()

    # Call compare solvers automatically unless deactivated
    if not args.no_compare:
        train_tasks = []
        validation_tasks = []

        if args.size == 7:
            train_tasks.append(("Size 7 Training Set (Single Solution)", "-s 1", s7_train))
            train_tasks.append(("Size 7 Training Set (Full Enumeration)", "-s 0", s7_train))
            validation_tasks.append(("Size 7 Validation Set (Single Solution)", "-s 1", s7_val))
            validation_tasks.append(("Size 7 Validation Set (Full Enumeration)", "-s 0", s7_val))

        elif args.size == 8:
            train_tasks.append(("Size 8 Training Set (Single Solution)", "-s 1", s8_single_train))
            train_tasks.append(("Size 8 Training Set (Full Enumeration)", "-s 0", s8_enum_train))
            validation_tasks.append(("Size 8 Validation Set (Single Solution)", "-s 1", s8_single_val))
            validation_tasks.append(("Size 8 Validation Set (Full Enumeration)", "-s 0", s8_enum_val))

        elif args.size == 9:
            train_tasks.append(("Size 9 Level 1 Training Set", "-s 1", s9_lvl1_train))
            train_tasks.append(("Size 9 Level 2 Training Set", "-s 1", s9_lvl2_train))
            train_tasks.append(("Size 9 Level 3 Training Set", "-s 1", s9_lvl3_train))
            validation_tasks.append(("Size 9 Level 1 Validation Set", "-s 1", s9_lvl1_val))
            validation_tasks.append(("Size 9 Level 2 Validation Set", "-s 1", s9_lvl2_val))
            validation_tasks.append(("Size 9 Level 3 Validation Set", "-s 1", s9_lvl3_val))

        # Construct comparison log paths if main log is provided
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

if __name__ == "__main__":
    main()
