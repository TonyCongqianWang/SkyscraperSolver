#!/usr/bin/env python3
import os
import sys
import re

MATH_VARS = [
    ("g_weight_cell_constr_ratio_le7", "WEIGHT_CELL_CONSTR_RATIO_LE7", "double"),
    ("g_weight_cell_constr_ratio_s8", "WEIGHT_CELL_CONSTR_RATIO_S8", "double"),
    ("g_weight_cell_constr_ratio_s9", "WEIGHT_CELL_CONSTR_RATIO_S9", "double"),
    ("g_sel_weight_cell_constr_ratio_le7", "SEL_WEIGHT_CELL_CONSTR_RATIO_LE7", "double"),
    ("g_sel_weight_cell_constr_ratio_s8", "SEL_WEIGHT_CELL_CONSTR_RATIO_S8", "double"),
    ("g_sel_weight_cell_constr_ratio_s9", "SEL_WEIGHT_CELL_CONSTR_RATIO_S9", "double"),
    ("g_weight_total_scale_le7", "WEIGHT_TOTAL_SCALE_LE7", "double"),
    ("g_weight_total_scale_s8", "WEIGHT_TOTAL_SCALE_S8", "double"),
    ("g_weight_total_scale_s9", "WEIGHT_TOTAL_SCALE_S9", "double"),
    ("g_global_entropy_unset_bias_le7", "GLOBAL_ENTROPY_UNSET_BIAS_LE7", "double"),
    ("g_global_entropy_unset_bias_s8", "GLOBAL_ENTROPY_UNSET_BIAS_S8", "double"),
    ("g_global_entropy_unset_bias_s9", "GLOBAL_ENTROPY_UNSET_BIAS_S9", "double"),
    ("g_sel_power_le7", "SEL_POWER_LE7", "double"),
    ("g_sel_power_s8", "SEL_POWER_S8", "double"),
    ("g_sel_power_s9", "SEL_POWER_S9", "double"),
    ("g_lookahead_score_weight_split0_le7", "LOOKAHEAD_SCORE_WEIGHT_SPLIT0_LE7", "double"),
    ("g_lookahead_score_weight_split0_s8", "LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S8", "double"),
    ("g_lookahead_score_weight_split0_s9", "LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S9", "double"),
    ("g_lookahead_score_weight_split1_le7", "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_LE7", "double"),
    ("g_lookahead_score_weight_split1_s8", "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S8", "double"),
    ("g_lookahead_score_weight_split1_s9", "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S9", "double"),
    ("g_lookahead_entropy_weight_le7", "LOOKAHEAD_ENTROPY_WEIGHT_LE7", "double"),
    ("g_lookahead_entropy_weight_s8", "LOOKAHEAD_ENTROPY_WEIGHT_S8", "double"),
    ("g_lookahead_entropy_weight_s9", "LOOKAHEAD_ENTROPY_WEIGHT_S9", "double"),
    ("g_depth_warp_0_le7", "DEPTH_WARP_0_LE7", "double"),
    ("g_depth_warp_0_s8", "DEPTH_WARP_0_S8", "double"),
    ("g_depth_warp_0_s9", "DEPTH_WARP_0_S9", "double"),
    ("g_depth_warp_1_le7", "DEPTH_WARP_1_LE7", "double"),
    ("g_depth_warp_1_s8", "DEPTH_WARP_1_S8", "double"),
    ("g_depth_warp_1_s9", "DEPTH_WARP_1_S9", "double"),
    ("g_depth_warp_2_le7", "DEPTH_WARP_2_LE7", "double"),
    ("g_depth_warp_2_s8", "DEPTH_WARP_2_S8", "double"),
    ("g_depth_warp_2_s9", "DEPTH_WARP_2_S9", "double"),
    ("g_lookahead_score_age_limit_ratio_le7", "LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_LE7", "double"),
    ("g_lookahead_score_age_limit_ratio_s8", "LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_S8", "double"),
    ("g_lookahead_score_age_limit_ratio_s9", "LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_S9", "double"),
]

KNOT_NAMES = ["p00", "p25", "p50", "p100"]

INT_BASE_VARS = [
    "min_entropy",
    "gac_min_entropy",
    "constr_min_entropy",
    "lookahead_continue_min_entropy",
    "gac_global_min_entropy",
    "constr_global_min_entropy",
    "lookahead_gac_global_min_entropy",
    "lookahead_constr_global_min_entropy",
]

INT_VARS = [
    ("g_root_min_entropy", "ROOT_MIN_ENTROPY", "int"),
    ("g_root_gac_min_entropy", "ROOT_GAC_MIN_ENTROPY", "int"),
    ("g_root_constr_min_entropy", "ROOT_CONSTR_MIN_ENTROPY", "int"),
    ("g_root_gac_global_min_entropy", "ROOT_GAC_GLOBAL_MIN_ENTROPY", "int"),
    ("g_root_constr_global_min_entropy", "ROOT_CONSTR_GLOBAL_MIN_ENTROPY", "int"),
    ("g_root_lookahead_gac_global_min_entropy", "ROOT_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", "int"),
    ("g_root_lookahead_constr_global_min_entropy", "ROOT_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", "int"),
    ("g_root_lookahead_continue_min_entropy", "ROOT_LOOKAHEAD_CONTINUE_MIN_ENTROPY", "int"),
]
for base in INT_BASE_VARS:
    for k in KNOT_NAMES:
        INT_VARS.append((f"g_{base}_{k}", f"{base.upper()}_{k.upper()}", "int"))

DOUBLE_BASE_VARS = [
    "lookahead_continue_slope",
    "period_coef_scale",
    "period_coef_unset",
    "period_tier_medium_mult",
    "period_tier_heavy_mult",
    "gac_local_min_entropy",
    "gac_local_max_entropy",
    "constr_local_min_entropy",
    "constr_local_max_entropy",
    "lookahead_gac_local_min_entropy",
    "lookahead_gac_local_max_entropy",
    "lookahead_constr_local_min_entropy",
    "lookahead_constr_local_max_entropy",
]

DOUBLE_VARS = [
    ("g_sel_period_coef_sqrt", "SEL_PERIOD_COEF_SQRT", "double"),
    ("g_sel_period_coef_inv", "SEL_PERIOD_COEF_INV", "double"),
    ("g_root_period_tier_complement_mult", "ROOT_PERIOD_TIER_COMPLEMENT_MULTIPLIER", "double"),
    ("g_root_lookahead_continue_slope", "ROOT_LOOKAHEAD_CONTINUE_SLOPE", "double"),
    ("g_root_period_coef_scale", "ROOT_PERIOD_COEF_SCALE", "double"),
    ("g_root_period_coef_unset", "ROOT_PERIOD_COEF_UNSET", "double"),
    ("g_root_period_tier_medium_mult", "ROOT_PERIOD_TIER_MEDIUM_MULTIPLIER", "double"),
    ("g_root_period_tier_heavy_mult", "ROOT_PERIOD_TIER_HEAVY_MULTIPLIER", "double"),
    ("g_root_gac_local_min_entropy", "ROOT_GAC_LOCAL_MIN_ENTROPY", "double"),
    ("g_root_gac_local_max_entropy", "ROOT_GAC_LOCAL_MAX_ENTROPY", "double"),
    ("g_root_constr_local_min_entropy", "ROOT_CONSTR_LOCAL_MIN_ENTROPY", "double"),
    ("g_root_constr_local_max_entropy", "ROOT_CONSTR_LOCAL_MAX_ENTROPY", "double"),
    ("g_root_lookahead_gac_local_min_entropy", "ROOT_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", "double"),
    ("g_root_lookahead_gac_local_max_entropy", "ROOT_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", "double"),
    ("g_root_lookahead_constr_local_min_entropy", "ROOT_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", "double"),
    ("g_root_lookahead_constr_local_max_entropy", "ROOT_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", "double"),
]
for base in DOUBLE_BASE_VARS:
    env_base = base.upper().replace("_MULT", "_MULTIPLIER")
    for k in KNOT_NAMES:
        DOUBLE_VARS.append((f"g_{base}_{k}", f"{env_base}_{k.upper()}", "double"))

FILES_CONFIGS = [
    ("src/params_math.c", MATH_VARS, "init_params_math_env"),
    ("src/params_int.c", INT_VARS, "init_params_int_env"),
    ("src/params_double.c", DOUBLE_VARS, "init_params_double_env"),
]

def apply_overrides_to_file(filepath, var_list, func_name):
    if not os.path.exists(filepath):
        print(f"Warning: file not found: {filepath}")
        return

    with open(filepath, "r") as f:
        content = f.read()

    var_values = {}
    for var_name, env_name, var_type in var_list:
        pattern = re.compile(rf'(?:const\s+)?(?:double|int)\s+{var_name}\s*=\s*([^;]+);')
        match = pattern.search(content)
        if match:
            var_values[var_name] = match.group(1).strip()
        else:
            print(f"Error: Could not find parameter declaration for '{var_name}' in '{filepath}'", file=sys.stderr)
            sys.exit(1)

    decl_lines = []
    env_lines = []

    for var_name, env_name, var_type in var_list:
        val = var_values[var_name]
        tabs = "\t\t" if var_type == "int" else "\t"
        decl_lines.append(f"{var_type}{tabs}{var_name} = {val};")
        conv = "atoi" if var_type == "int" else "atof"
        env_lines.append(f'\tval = getenv("{env_name}");\n\tif (val)\n\t\t{var_name} = {conv}(val);')

    env_body = "\n".join(env_lines)
    decl_body = "\n".join(decl_lines)

    extra_include = ""
    extra_call = ""

    func_code = f"""#include <stdlib.h>
{extra_include}
#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
__attribute__((constructor))
static void\t{func_name}(void)
{{
\tchar\t*val;

{env_body}{extra_call}
}}
#endif"""

    header_inc = f'#include "{os.path.basename(filepath).replace(".c", ".h")}"'
    new_content = f"""/* Tunable overrides active */
{header_inc}
{func_code}

{decl_body}
"""
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"Successfully applied overrides to {filepath}")

def unapply_overrides_from_file(filepath, var_list):
    if not os.path.exists(filepath):
        return

    with open(filepath, "r") as f:
        content = f.read()

    var_values = {}
    for var_name, env_name, var_type in var_list:
        pattern = re.compile(rf'(?:const\s+)?(?:double|int)\s+{var_name}\s*=\s*([^;]+);')
        match = pattern.search(content)
        if match:
            var_values[var_name] = match.group(1).strip()
        else:
            print(f"Error: Could not find parameter declaration for '{var_name}' in '{filepath}'", file=sys.stderr)
            sys.exit(1)

    decl_lines = []
    for var_name, env_name, var_type in var_list:
        val = var_values[var_name]
        tabs = "\t\t" if var_type == "int" else "\t"
        decl_lines.append(f"{var_type}{tabs}{var_name} = {val};")

    header_inc = f'#include "{os.path.basename(filepath).replace(".c", ".h")}"'
    decl_body = "\n".join(decl_lines)

    fname = os.path.basename(filepath)
    pad = 51 - len(fname)
    header_comment = f"""/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   {fname}{' ' * pad}:+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */"""

    new_content = f"{header_comment}\n\n{header_inc}\n\n{decl_body}\n"
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"Successfully unapplied overrides from {filepath}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply or unapply environment overrides to parameter C files.")
    parser.add_argument("--unapply", action="store_true", help="Remove overrides and restore original const configurations.")
    args = parser.parse_args()

    for filepath, var_list, func_name in FILES_CONFIGS:
        if args.unapply:
            unapply_overrides_from_file(filepath, var_list)
        else:
            apply_overrides_to_file(filepath, var_list, func_name)

if __name__ == "__main__":
    main()
