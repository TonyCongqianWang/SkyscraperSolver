#!/usr/bin/env python3
import os
import sys
import re

INT_VARS = []
for tier_lower, tier_upper in [("root", "ROOT"), ("shallow", "SHALLOW"), ("medium", "MEDIUM"), ("deep", "DEEP")]:
    INT_VARS.extend([
        (f"g_{tier_lower}_min_entropy", f"{tier_upper}_MIN_ENTROPY", "int"),
        (f"g_{tier_lower}_gac_min_entropy", f"{tier_upper}_GAC_MIN_ENTROPY", "int"),
        (f"g_{tier_lower}_constr_min_entropy", f"{tier_upper}_CONSTR_MIN_ENTROPY", "int"),
        (f"g_{tier_lower}_gac_global_min_entropy", f"{tier_upper}_GAC_GLOBAL_MIN_ENTROPY", "int"),
        (f"g_{tier_lower}_constr_global_min_entropy", f"{tier_upper}_CONSTR_GLOBAL_MIN_ENTROPY", "int"),
        (f"g_{tier_lower}_lookahead_gac_global_min_entropy", f"{tier_upper}_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", "int"),
        (f"g_{tier_lower}_lookahead_constr_global_min_entropy", f"{tier_upper}_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", "int"),
    ])

DOUBLE_VARS = [
    ("g_routing_shallow_ratio", "ROUTING_SHALLOW_RATIO", "double"),
    ("g_routing_medium_ratio", "ROUTING_MEDIUM_RATIO", "double"),
    ("g_sel_period_coef_sqrt", "SEL_PERIOD_COEF_SQRT", "double"),
    ("g_sel_period_coef_inv", "SEL_PERIOD_COEF_INV", "double"),
]
for tier_lower, tier_upper in [("root", "ROOT"), ("shallow", "SHALLOW"), ("medium", "MEDIUM"), ("deep", "DEEP")]:
    DOUBLE_VARS.extend([
        (f"g_{tier_lower}_lookahead_downgrade_fraction", f"{tier_upper}_LOOKAHEAD_DOWNGRADE_FRACTION", "double"),
        (f"g_{tier_lower}_period_coef_scale", f"{tier_upper}_PERIOD_COEF_SCALE", "double"),
        (f"g_{tier_lower}_period_coef_unset", f"{tier_upper}_PERIOD_COEF_UNSET", "double"),
        (f"g_{tier_lower}_period_tier_medium_mult", f"{tier_upper}_PERIOD_TIER_MEDIUM_MULTIPLIER", "double"),
        (f"g_{tier_lower}_period_tier_heavy_mult", f"{tier_upper}_PERIOD_TIER_HEAVY_MULTIPLIER", "double"),
        (f"g_{tier_lower}_gac_local_min_entropy", f"{tier_upper}_GAC_LOCAL_MIN_ENTROPY", "double"),
        (f"g_{tier_lower}_gac_local_max_entropy", f"{tier_upper}_GAC_LOCAL_MAX_ENTROPY", "double"),
        (f"g_{tier_lower}_constr_local_min_entropy", f"{tier_upper}_CONSTR_LOCAL_MIN_ENTROPY", "double"),
        (f"g_{tier_lower}_constr_local_max_entropy", f"{tier_upper}_CONSTR_LOCAL_MAX_ENTROPY", "double"),
        (f"g_{tier_lower}_lookahead_gac_local_min_entropy", f"{tier_upper}_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", "double"),
        (f"g_{tier_lower}_lookahead_gac_local_max_entropy", f"{tier_upper}_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", "double"),
        (f"g_{tier_lower}_lookahead_constr_local_min_entropy", f"{tier_upper}_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", "double"),
        (f"g_{tier_lower}_lookahead_constr_local_max_entropy", f"{tier_upper}_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", "double"),
    ])

FILES_CONFIGS = [
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
        decl_lines.append(f"{var_type}\t{var_name} = {val};")
        conv = "atoi" if var_type == "int" else "atof"
        env_lines.append(f'\tval = getenv("{env_name}");\n\tif (val)\n\t\t{var_name} = {conv}(val);')

    env_body = "\n".join(env_lines)
    decl_body = "\n".join(decl_lines)

    func_code = f"""#include <stdlib.h>

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
__attribute__((constructor))
static void	{func_name}(void)
{{
	char	*val;

{env_body}
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
        decl_lines.append(f"{var_type}\t{var_name} = {val};")

    header_inc = f'#include "{os.path.basename(filepath).replace(".c", ".h")}"'
    decl_body = "\n".join(decl_lines)

    header_comment = """/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   """ + os.path.basename(filepath) + """                               :+:      :+:    :+:   */
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
