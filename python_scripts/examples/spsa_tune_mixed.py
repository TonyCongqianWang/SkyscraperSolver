#!/usr/bin/env python3
import subprocess
import time
import concurrent.futures
import os
import sys
import random
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

def resolve_binary_path(path):
    if not path:
        return path
    if os.name == 'nt' or sys.platform.startswith('win'):
        if not path.lower().endswith('.exe'):
            if os.path.exists(path + '.exe'):
                return path + '.exe'
    return path

BIN_CURR = resolve_binary_path(os.path.join(ROOT_DIR, "skyscraper_solver"))

PATH_S7 = os.path.join(ROOT_DIR, "benchmark_sets", "benchmarkSet7_easy500.txt")
PATH_S8 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_all_solutions", "benchmarkSet8_medium.txt")
PATH_S9 = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated.txt")
PATH_S9_HARDER = os.path.join(ROOT_DIR, "benchmark_sets", "calibrated_single_solution", "benchmarkSet9_calibrated_harder.txt")

# Parameters Metadata starting from SPSA Tuned config: (name, min, max, default, type)
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
    # Load all files and split into train/val
    with open(PATH_S7, "r") as f:
        s7_all = [l.strip().strip('"') for l in f if l.strip()]
        s7_clues = s7_all[:400]
    with open(PATH_S8, "r") as f:
        s8_all = [l.strip().strip('"') for l in f if l.strip()]
        s8_clues = s8_all[:146]
    with open(PATH_S9, "r") as f:
        s9_raw = [l.strip().strip('"') for l in f if l.strip()]
        
    s9_groups = {}
    for clue in s9_raw:
        key = canonize(clue)
        if key not in s9_groups:
            s9_groups[key] = []
        s9_groups[key].append(clue)
    s9_groups = list(s9_groups.values())
    s9_train_groups = s9_groups[:int(len(s9_groups)*0.8)]
    
    # Load harder set and group
    with open(PATH_S9_HARDER, "r") as f:
        s9_harder_raw = [l.strip().strip('"') for l in f if l.strip()]
    s9_harder_groups = {}
    for clue in s9_harder_raw:
        key = canonize(clue)
        if key not in s9_harder_groups:
            s9_harder_groups[key] = []
        s9_harder_groups[key].append(clue)
    s9_harder_groups = list(s9_harder_groups.values())
    
    # S9 Harder train splits (use 50% of the available groups)
    s9_harder_train_groups = s9_harder_groups[:int(len(s9_harder_groups) * 0.5)]
    
    print(f"Loaded train datasets:")
    print(f"  S7 Easy:       {len(s7_clues)} puzzles")
    print(f"  S8 Medium:     {len(s8_clues)} puzzles")
    print(f"  S9 Calibrated: {len(s9_train_groups)} groups")
    print(f"  S9 Harder v2:  {len(s9_harder_train_groups)} groups")
    
    theta = get_default_theta()
    
    # SPSA Hyperparameters
    alpha = 0.602
    gamma = 0.101
    c = 0.03
    a = 0.005
    A = 40
    iterations = 400
    
    # Stochastic Weight Averaging (SWA) parameters
    swa_theta = [0.0] * len(theta)
    swa_count = 0
    swa_start = int(iterations * 0.8)  # Start SWA over the last 20% of iterations (e.g. iteration 320)
    
    # Reference baselines for normalization
    ref_scale_s7 = 0.01
    ref_scale_s8 = 0.20
    ref_scale_s9 = 0.30
    ref_scale_s9_hard = 2.50
    
    best_loss = float('inf')
    best_theta = list(theta)
    
    print("Running multi-task SPSA tuning to prioritize harder instances (starting from Heavy Pruning baseline)...")
    
    for k in range(1, iterations + 1):
        ak = a / ((k + A) ** alpha)
        ck = c / (k ** gamma)
        
        # Sample subsets (larger batches for stability)
        sampled_s7 = random.sample(s7_clues, 8)
        sampled_s8 = random.sample(s8_clues, 8)
        sampled_s9_groups = random.sample(s9_train_groups, 4)
        sampled_s9_harder_groups = random.sample(s9_harder_train_groups, 4)
        
        sampled_s9 = []
        for g in sampled_s9_groups:
            sampled_s9.extend(g)
            
        sampled_s9_hard = []
        for g in sampled_s9_harder_groups:
            sampled_s9_hard.extend(g)
            
        # Define tasks
        tasks_s7 = [("-s 0", clue) for clue in sampled_s7]
        tasks_s8 = [("-s 0", clue) for clue in sampled_s8]
        tasks_s9 = [("-s 1", clue) for clue in sampled_s9]
        tasks_s9_hard = [("-s 1", clue) for clue in sampled_s9_hard]
        
        # Perturbation direction
        delta = [random.choice([-1.0, 1.0]) for _ in range(len(theta))]
        
        def get_mixed_loss(config_theta):
            env = get_env_for_theta(config_theta)
            
            t7, n7 = evaluate_subset(env, tasks_s7)
            t8, n8 = evaluate_subset(env, tasks_s8)
            t9, n9 = evaluate_subset(env, tasks_s9)
            th, nh = evaluate_subset(env, tasks_s9_hard)
            
            # SGM with high shift values to weigh more towards arithmetic mean
            sgm_t7 = shifted_geo_mean(t7, 10.0)
            sgm_n7 = shifted_geo_mean(n7, 10000.0)
            loss7 = (sgm_t7 + 5e-6 * sgm_n7) / ref_scale_s7
            
            sgm_t8 = shifted_geo_mean(t8, 10.0)
            sgm_n8 = shifted_geo_mean(n8, 100000.0)
            loss8 = (sgm_t8 + 5e-6 * sgm_n8) / ref_scale_s8
            
            sgm_t9 = shifted_geo_mean(t9, 10.0)
            sgm_n9 = shifted_geo_mean(n9, 50000.0)
            loss9 = (sgm_t9 + 5e-6 * sgm_n9) / ref_scale_s9
            
            sgm_th = shifted_geo_mean(th, 10.0)
            sgm_nh = shifted_geo_mean(nh, 250000.0)
            loss_hard = (sgm_th + 5e-6 * sgm_nh) / ref_scale_s9_hard
            
            # Weighted loss prioritizing S9 Harder (8.0x weight)
            total_loss = 0.2 * loss7 + 0.5 * loss8 + 1.0 * loss9 + 8.0 * loss_hard
            return total_loss, (sgm_t8, sgm_n8, sgm_t9, sgm_n9, sgm_th, sgm_nh)
            
        # Perturbed plus
        theta_plus = [max(0.0, min(1.0, theta[i] + ck * delta[i])) for i in range(len(theta))]
        loss_plus, _ = get_mixed_loss(theta_plus)
        
        # Perturbed minus
        theta_minus = [max(0.0, min(1.0, theta[i] - ck * delta[i])) for i in range(len(theta))]
        loss_minus, _ = get_mixed_loss(theta_minus)
        
        # Gradient
        grad = []
        for i in range(len(theta)):
            g_i = (loss_plus - loss_minus) / (2.0 * ck * delta[i])
            grad.append(g_i)
            
        # Update with step size capping (gradient clipping) to prevent timeout explosion
        max_step = 0.02
        theta_next = []
        for i in range(len(theta)):
            step_i = ak * grad[i]
            step_c = max(-max_step, min(max_step, step_i))
            val = max(0.0, min(1.0, theta[i] - step_c))
            theta_next.append(val)
        theta = theta_next
        
        # Accumulate SWA weights
        if k >= swa_start:
            swa_count += 1
            for i in range(len(theta)):
                swa_theta[i] += theta[i]
        
        # Monitor progress
        loss_curr, stats = get_mixed_loss(theta)
        
        if loss_curr < best_loss:
            best_loss = loss_curr
            best_theta = list(theta)
            
        print(f"Iteration {k:2d} | Loss: {loss_curr:.3f} | Best Loss: {best_loss:.3f} | S9 SGM Nodes: {stats[3]:.1f} | Harder SGM Nodes: {stats[5]:.1f}")
        
    print("\nMulti-task tuning completed!")
    print(f"Best Loss achieved (single iteration): {best_loss:.3f}")
    
    # Compute SWA averaged parameters
    if swa_count > 0:
        theta_final = [x / swa_count for x in swa_theta]
        print(f"Computed Stochastic Weight Average (SWA) over the last {swa_count} iterations.")
    else:
        theta_final = list(theta)
        
    phys_best = get_physical_params(theta_final)
    print("\nOptimal Generalizing Parameter Values (SWA):")
    print("=======================================")
    for name, val in phys_best.items():
        print(f"{name} = {val}")
        
    # Ensure scratch directory exists
    os.makedirs("scratch", exist_ok=True)
    
    # Resolve a unique filename to prevent overwriting previous SPSA wins
    base_path = "scratch/spsa_winners_mixed"
    ext = ".txt"
    filename = f"{base_path}{ext}"
    if os.path.exists(filename):
        idx = 0
        while os.path.exists(f"{base_path}_{idx}{ext}"):
            idx += 1
        filename = f"{base_path}_{idx}{ext}"
        
    with open(filename, "w") as f:
        f.write("SPSA WINNING GENERALIZED HYPERPARAMETERS (SWA)\n")
        f.write("==============================================\n")
        for name, val in phys_best.items():
            f.write(f"#define {name} {val}\n")
            
    print(f"\nOptimal SWA generalizing definitions written to {filename}")

if __name__ == "__main__":
    main()
