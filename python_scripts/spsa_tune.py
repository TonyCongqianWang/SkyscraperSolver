#!/usr/bin/env python3
import subprocess
import time
import concurrent.futures
import os
import sys
import random
import math
import argparse

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
PATH_S7 = os.path.join(ROOT_DIR, "benchmark_sets", "benchmarkSet7_easy500.txt")

# Size 8 calibrated files
PATH_S8_EASY = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_easy.txt")
PATH_S8_MED = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_medium.txt")
PATH_S8_HARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_hard.txt")
PATH_S8_XHARD = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_xhard.txt")

# Size 9 calibrated files
PATH_S9 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated.txt")
PATH_S9_HARDER = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated_harder.txt")

# Parameters Metadata: (name, min, max, default, type)
PARAM_METADATA = [
    # ROUTING
    ("ROUTING_SHALLOW_RATIO", 0.0, 0.3, 0.05124164111312287, float),
    ("ROUTING_MEDIUM_RATIO", 0.0, 0.5, 0.3346467565940329, float),
    # ROOT
    ("ROOT_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.4573468754984318, float),
    ("ROOT_CONSTR_MIN_UNSET", 0.0, 1.0, 0.6912740782705177, float),
    ("ROOT_CONSTR_MAX_UNSET", 0.0, 1.0, 0.4639806021442083, float),
    ("ROOT_PERIOD_BASE", 1, 100, 64, int),
    ("ROOT_PERIOD_COEF1", 0, 10000, 2558, int),
    ("ROOT_PERIOD_COEF2", 0, 150000, 133833, int),
    # SHALLOW
    ("SHALLOW_MIN_UNSET", 0.0, 0.5, 0.4160997230316314, float),
    ("SHALLOW_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.6113333594264682, float),
    ("SHALLOW_CONSTR_MIN_UNSET", 0.0, 1.0, 0.429597122772291, float),
    ("SHALLOW_CONSTR_MAX_UNSET", 0.0, 1.0, 0.8000990550603081, float),
    ("SHALLOW_PERIOD_BASE", 1, 200, 6, int),
    ("SHALLOW_PERIOD_COEF1", 0, 15000, 3692, int),
    ("SHALLOW_PERIOD_COEF2", 0, 150000, 19237, int),
    # MEDIUM
    ("MEDIUM_MIN_UNSET", 0.0, 0.5, 0.3674707507630957, float),
    ("MEDIUM_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.1470424520508711, float),
    ("MEDIUM_CONSTR_MIN_UNSET", 0.0, 1.0, 0.9879694462689003, float),
    ("MEDIUM_CONSTR_MAX_UNSET", 0.0, 1.0, 0.9151172903633186, float),
    ("MEDIUM_PERIOD_BASE", 1, 300, 67, int),
    ("MEDIUM_PERIOD_COEF1", 0, 10000, 3340, int),
    ("MEDIUM_PERIOD_COEF2", 0, 150000, 116637, int),
    # DEEP
    ("DEEP_MIN_UNSET", 0.0, 0.5, 0.0893668491434967, float),
    ("DEEP_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.23826264102249042, float),
    ("DEEP_CONSTR_MIN_UNSET", 0.0, 1.0, 1.0, float),
    ("DEEP_CONSTR_MAX_UNSET", 0.0, 1.0, 0.3968727769990099, float),
    ("DEEP_PERIOD_BASE", 1, 400, 245, int),
    ("DEEP_PERIOD_COEF1", 0, 20000, 12365, int),
    ("DEEP_PERIOD_COEF2", 0, 150000, 101540, int),
]

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

def evaluate_subset(env, tasks, max_workers=4):
    times = []
    nodes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_solver_instance, env, opt, clue) for opt, clue in tasks]
        for fut in futures:
            t, n = fut.result()
            times.append(t)
            nodes.append(n)
    return times, nodes

def get_env_for_theta(theta):
    env = os.environ.copy()
    for val, (name, pmin, pmax, default, ptype) in zip(theta, PARAM_METADATA):
        phys_val = pmin + val * (pmax - pmin)
        if ptype is int:
            phys_val = int(round(phys_val))
        env[name] = str(phys_val)
    return env

def get_physical_params(theta):
    phys = {}
    for val, (name, pmin, pmax, default, ptype) in zip(theta, PARAM_METADATA):
        phys_val = pmin + val * (pmax - pmin)
        if ptype is int:
            phys_val = int(round(phys_val))
        phys[name] = phys_val
    return phys

def get_default_theta():
    theta = []
    for name, pmin, pmax, default, ptype in PARAM_METADATA:
        val = (default - pmin) / (pmax - pmin)
        theta.append(val)
    return theta

def main():
    parser = argparse.ArgumentParser(description="Run SPSA tuning for a specific board size.")
    parser.add_argument("--size", type=int, choices=[7, 8, 9], required=True, help="Solver puzzle size to optimize")
    parser.add_argument("--iterations", type=int, default=400, help="Number of SPSA tuning iterations")
    parser.add_argument("--log", default=None, help="Optional file path to log terminal outputs")
    parser.add_argument("--no-compare", action="store_true", help="Deactivate calling the compare solvers routine at the end of SPSA automatically")
    args = parser.parse_args()
    
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
        mid_s7 = len(s7_all) // 2
        s7_train = s7_all[:mid_s7]
        s7_val = s7_all[mid_s7:]
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
        s9_calib = read_clues(PATH_S9)
        s9_harder = read_clues(PATH_S9_HARDER)
        
        s9_calib_train, s9_calib_val = get_deterministic_split(s9_calib, 0.7)
        s9_harder_train, s9_harder_val = get_deterministic_split(s9_harder, 0.7)
        
        log_print(f"Loaded Size 9 datasets:")
        log_print(f"  Calibrated train: {len(s9_calib_train)} clues (val: {len(s9_calib_val)})")
        log_print(f"  Harder train:     {len(s9_harder_train)} clues (val: {len(s9_harder_val)})")

    # 2. SPSA Hyperparameters
    alpha = 0.602
    gamma = 0.101
    c = 0.03
    a = 0.005
    A = 40
    iterations = args.iterations
    
    theta = get_default_theta()
    swa_theta = [0.0] * len(theta)
    swa_count = 0
    swa_start = int(iterations * 0.8)
    
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
    
    ref_scale_s9_calib_time = 0.20
    ref_scale_s9_calib_nodes = 20000.0
    ref_scale_s9_harder_time = 1.50
    ref_scale_s9_harder_nodes = 200000.0
    
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
            sampled_single = random.sample(s7_train, min(len(s7_train), 8))
            sampled_enum = random.sample(s7_train, min(len(s7_train), 8))
            tasks_single = [("-s 1", clue) for clue in sampled_single]
            tasks_enum = [("-s 0", clue) for clue in sampled_enum]
            
            def get_loss(config_theta):
                env = get_env_for_theta(config_theta)
                t_single, n_single = evaluate_subset(env, tasks_single)
                t_enum, n_enum = evaluate_subset(env, tasks_enum)
                
                sgm_t_s = shifted_geo_mean(t_single, 0.1)
                sgm_n_s = shifted_geo_mean(n_single, 1000.0)
                
                sgm_t_e = shifted_geo_mean(t_enum, 0.1)
                sgm_n_e = shifted_geo_mean(n_enum, 1000.0)
                
                loss_time = 1.0 * (sgm_t_s / ref_scale_s7_single_time) + 3.0 * (sgm_t_e / ref_scale_s7_enum_time)
                loss_nodes = 1.0 * (sgm_n_s / ref_scale_s7_single_nodes) + 3.0 * (sgm_n_e / ref_scale_s7_enum_nodes)
                
                return loss_time, loss_nodes, (sgm_t_s, sgm_n_s, sgm_t_e, sgm_n_e)
                
        elif args.size == 8:
            sampled_s8_single_easy_med = random.sample(easy_train + med_train, min(len(easy_train + med_train), 4))
            sampled_s8_single_hard_xhard = random.sample(hard_train + xhard_train, min(len(hard_train + xhard_train), 4))
            sampled_s8_enum = random.sample(easy_train + med_train, min(len(easy_train + med_train), 8))
            
            tasks_single_easy_med = [("-s 1", clue) for clue in sampled_s8_single_easy_med]
            tasks_single_hard_xhard = [("-s 1", clue) for clue in sampled_s8_single_hard_xhard]
            tasks_enum = [("-s 0", clue) for clue in sampled_s8_enum]
            
            def get_loss(config_theta):
                env = get_env_for_theta(config_theta)
                t_s_em, n_s_em = evaluate_subset(env, tasks_single_easy_med)
                t_s_hx, n_s_hx = evaluate_subset(env, tasks_single_hard_xhard)
                t_e_em, n_e_em = evaluate_subset(env, tasks_enum)
                
                sgm_t_s_em = shifted_geo_mean(t_s_em, 0.1)
                sgm_n_s_em = shifted_geo_mean(n_s_em, 1000.0)
                
                sgm_t_s_hx = shifted_geo_mean(t_s_hx, 0.1)
                sgm_n_s_hx = shifted_geo_mean(n_s_hx, 1000.0)
                
                sgm_t_e_em = shifted_geo_mean(t_e_em, 0.1)
                sgm_n_e_em = shifted_geo_mean(n_e_em, 1000.0)
                
                loss_time = 0.2 * (sgm_t_s_em / ref_scale_s8_single_easy_med_time) + 1.0 * (sgm_t_s_hx / ref_scale_s8_single_hard_xhard_time) + 4.0 * (sgm_t_e_em / ref_scale_s8_enum_easy_med_time)
                loss_nodes = 0.2 * (sgm_n_s_em / ref_scale_s8_single_easy_med_nodes) + 1.0 * (sgm_n_s_hx / ref_scale_s8_single_hard_xhard_nodes) + 4.0 * (sgm_n_e_em / ref_scale_s8_enum_easy_med_nodes)
                
                return loss_time, loss_nodes, (sgm_t_s_hx, sgm_n_s_hx, sgm_t_e_em, sgm_n_e_em)
                
        elif args.size == 9:
            sampled_calib = random.sample(s9_calib_train, min(len(s9_calib_train), 8))
            sampled_harder = random.sample(s9_harder_train, min(len(s9_harder_train), 8))
            
            tasks_calib = [("-s 1", clue) for clue in sampled_calib]
            tasks_harder = [("-s 1", clue) for clue in sampled_harder]
            
            def get_loss(config_theta):
                env = get_env_for_theta(config_theta)
                t_c, n_c = evaluate_subset(env, tasks_calib)
                t_h, n_h = evaluate_subset(env, tasks_harder)
                
                sgm_t_c = shifted_geo_mean(t_c, 0.1)
                sgm_n_c = shifted_geo_mean(n_c, 1000.0)
                
                sgm_t_h = shifted_geo_mean(t_h, 0.1)
                sgm_n_h = shifted_geo_mean(n_h, 1000.0)
                
                loss_time = 1.0 * (sgm_t_c / ref_scale_s9_calib_time) + 8.0 * (sgm_t_h / ref_scale_s9_harder_time)
                loss_nodes = 1.0 * (sgm_n_c / ref_scale_s9_calib_nodes) + 8.0 * (sgm_n_h / ref_scale_s9_harder_nodes)
                
                return loss_time, loss_nodes, (sgm_t_c, sgm_n_c, sgm_t_h, sgm_n_h)
                
        delta = [random.choice([-1.0, 1.0]) for _ in range(len(theta))]
        
        # Perturbed plus
        theta_plus = [max(0.0, min(1.0, theta[i] + ck * delta[i])) for i in range(len(theta))]
        loss_time_plus, loss_nodes_plus, _ = get_loss(theta_plus)
        
        # Perturbed minus
        theta_minus = [max(0.0, min(1.0, theta[i] - ck * delta[i])) for i in range(len(theta))]
        loss_time_minus, loss_nodes_minus, _ = get_loss(theta_minus)
        
        # SPSA Gradients
        grad_time = []
        grad_nodes = []
        for i in range(len(theta)):
            gt_i = (loss_time_plus - loss_time_minus) / (2.0 * ck * delta[i])
            gn_i = (loss_nodes_plus - loss_nodes_minus) / (2.0 * ck * delta[i])
            grad_time.append(gt_i)
            grad_nodes.append(gn_i)
            
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
        theta = theta_next
        
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
            log_print(f"Iter {k:3d} | Loss(T/N): {loss_time_curr:.3f}/{loss_nodes_curr:.3f} | GradNorm(T/N): {grad_time_norm:.4f}/{grad_nodes_norm:.4f} | S9 Calib t: {stats[0]:.4f}s n: {stats[1]:.0f} | S9 Harder t: {stats[2]:.4f}s n: {stats[3]:.0f}")
            
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
        
    # Write to winners file
    os.makedirs(os.path.join(ROOT_DIR, "scratch"), exist_ok=True)
    base_path = f"scratch/spsa_winners_s{args.size}"
    ext = ".txt"
    filename = os.path.join(ROOT_DIR, f"{base_path}{ext}")
    if os.path.exists(filename):
        idx = 0
        while os.path.exists(os.path.join(ROOT_DIR, f"{base_path}_{idx}{ext}")):
            idx += 1
        filename = os.path.join(ROOT_DIR, f"{base_path}_{idx}{ext}")
        
    with open(filename, "w") as f:
        f.write(f"SPSA WINNING PARAMETERS FOR SIZE {args.size} (SWA)\n")
        f.write("==============================================\n")
        for name, val in phys_best.items():
            f.write(f"#define {name} {val}\n")
            
    log_print(f"\nOptimal generalizing definitions written to {filename}")
    
    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.close()
        
    # Call compare solvers automatically unless deactivated
    if not args.no_compare:
        validation_tasks = []
        if args.size == 7:
            validation_tasks.append(("Size 7 Validation Set (Single Solution)", "-s 1", s7_val))
            validation_tasks.append(("Size 7 Validation Set (Full Enumeration)", "-s 0", s7_val))
        elif args.size == 8:
            validation_tasks.append(("Size 8 Validation Set (Single Solution)", "-s 1", s8_single_val))
            validation_tasks.append(("Size 8 Validation Set (Full Enumeration)", "-s 0", s8_enum_val))
        elif args.size == 9:
            validation_tasks.append(("Size 9 Calibrated Validation Groups (Held-out)", "-s 1", s9_calib_val))
            validation_tasks.append(("Size 9 Harder Calibrated Validation Groups (Held-out)", "-s 1", s9_harder_val))
            
        import compare_performance
        compare_performance.run_comparison(
            validation_tasks=validation_tasks,
            baseline_bin=BIN_BASELINE,
            optimized_bin=BIN_CURR,
            extra_bin=None,
            tuned_env=get_env_for_theta(theta_final)
        )

if __name__ == "__main__":
    main()
