#!/usr/bin/env python3
import os
import sys
import re

def make_tier_config(tier_lower, tier_upper):
    return (f"src/prune_strat_{tier_lower}.c", {
        "var_names": [
            "g_min_entropy_threshold", "g_gac_min_entropy", "g_constr_min_entropy",
            "g_lookahead_downgrade_fraction",
            "g_period_coef_sqrt", "g_period_coef_inv", "g_period_coef_unset",
            "g_gac_local_min_unset", "g_gac_local_max_unset", "g_gac_global_min_entropy",
            "g_constr_local_min_unset", "g_constr_local_max_unset", "g_constr_global_min_entropy",
            "g_lookahead_gac_local_min_unset", "g_lookahead_gac_local_max_unset", "g_lookahead_gac_global_min_entropy",
            "g_lookahead_constr_local_min_unset", "g_lookahead_constr_local_max_unset", "g_lookahead_constr_global_min_entropy"
        ],
        "target_vars_template": """static const int		g_min_entropy_threshold = {g_min_entropy_threshold};
static const int		g_gac_min_entropy = {g_gac_min_entropy};
static const int		g_constr_min_entropy = {g_constr_min_entropy};
static const double		g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static const double		g_period_coef_sqrt = {g_period_coef_sqrt};
static const double		g_period_coef_inv = {g_period_coef_inv};
static const double		g_period_coef_unset = {g_period_coef_unset};
static const double		g_gac_local_min_unset = {g_gac_local_min_unset};
static const double		g_gac_local_max_unset = {g_gac_local_max_unset};
static const int		g_gac_global_min_entropy = {g_gac_global_min_entropy};
static const double		g_constr_local_min_unset = {g_constr_local_min_unset};
static const double		g_constr_local_max_unset = {g_constr_local_max_unset};
static const int		g_constr_global_min_entropy = {g_constr_global_min_entropy};
static const double		g_lookahead_gac_local_min_unset = {g_lookahead_gac_local_min_unset};
static const double		g_lookahead_gac_local_max_unset = {g_lookahead_gac_local_max_unset};
static const int		g_lookahead_gac_global_min_entropy = {g_lookahead_gac_global_min_entropy};
static const double		g_lookahead_constr_local_min_unset = {g_lookahead_constr_local_min_unset};
static const double		g_lookahead_constr_local_max_unset = {g_lookahead_constr_local_max_unset};
static const int		g_lookahead_constr_global_min_entropy = {g_lookahead_constr_global_min_entropy};""",
        "replacement_vars_template": f"""#include <stdlib.h>

static int		g_min_entropy_threshold = {{g_min_entropy_threshold}};
static int		g_gac_min_entropy = {{g_gac_min_entropy}};
static int		g_constr_min_entropy = {{g_constr_min_entropy}};
static double	g_lookahead_downgrade_fraction = {{g_lookahead_downgrade_fraction}};
static double	g_period_coef_sqrt = {{g_period_coef_sqrt}};
static double	g_period_coef_inv = {{g_period_coef_inv}};
static double	g_period_coef_unset = {{g_period_coef_unset}};
static double	g_gac_local_min_unset = {{g_gac_local_min_unset}};
static double	g_gac_local_max_unset = {{g_gac_local_max_unset}};
static int		g_gac_global_min_entropy = {{g_gac_global_min_entropy}};
static double	g_constr_local_min_unset = {{g_constr_local_min_unset}};
static double	g_constr_local_max_unset = {{g_constr_local_max_unset}};
static int		g_constr_global_min_entropy = {{g_constr_global_min_entropy}};
static double	g_lookahead_gac_local_min_unset = {{g_lookahead_gac_local_min_unset}};
static double	g_lookahead_gac_local_max_unset = {{g_lookahead_gac_local_max_unset}};
static int		g_lookahead_gac_global_min_entropy = {{g_lookahead_gac_global_min_entropy}};
static double	g_lookahead_constr_local_min_unset = {{g_lookahead_constr_local_min_unset}};
static double	g_lookahead_constr_local_max_unset = {{g_lookahead_constr_local_max_unset}};
static int		g_lookahead_constr_global_min_entropy = {{g_lookahead_constr_global_min_entropy}};

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{{{{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("{tier_upper}_MIN_ENTROPY");
	if (val)
		g_min_entropy_threshold = atoi(val);
	val = getenv("{tier_upper}_GAC_MIN_ENTROPY");
	if (val)
		g_gac_min_entropy = atoi(val);
	val = getenv("{tier_upper}_CONSTR_MIN_ENTROPY");
	if (val)
		g_constr_min_entropy = atoi(val);
	val = getenv("{tier_upper}_LOOKAHEAD_DOWNGRADE_FRACTION");
	if (val)
		g_lookahead_downgrade_fraction = atof(val);
	val = getenv("{tier_upper}_PERIOD_COEF_SQRT");
	if (val)
		g_period_coef_sqrt = atof(val);
	val = getenv("{tier_upper}_PERIOD_COEF_INV");
	if (val)
		g_period_coef_inv = atof(val);
	val = getenv("{tier_upper}_PERIOD_COEF_UNSET");
	if (val)
		g_period_coef_unset = atof(val);
	val = getenv("{tier_upper}_GAC_LOCAL_MIN_UNSET");
	if (val)
		g_gac_local_min_unset = atof(val);
	val = getenv("{tier_upper}_GAC_LOCAL_MAX_UNSET");
	if (val)
		g_gac_local_max_unset = atof(val);
	val = getenv("{tier_upper}_GAC_GLOBAL_MIN_ENTROPY");
	if (val)
		g_gac_global_min_entropy = atoi(val);
	val = getenv("{tier_upper}_CONSTR_LOCAL_MIN_UNSET");
	if (val)
		g_constr_local_min_unset = atof(val);
	val = getenv("{tier_upper}_CONSTR_LOCAL_MAX_UNSET");
	if (val)
		g_constr_local_max_unset = atof(val);
	val = getenv("{tier_upper}_CONSTR_GLOBAL_MIN_ENTROPY");
	if (val)
		g_constr_global_min_entropy = atoi(val);
	val = getenv("{tier_upper}_LOOKAHEAD_GAC_LOCAL_MIN_UNSET");
	if (val)
		g_lookahead_gac_local_min_unset = atof(val);
	val = getenv("{tier_upper}_LOOKAHEAD_GAC_LOCAL_MAX_UNSET");
	if (val)
		g_lookahead_gac_local_max_unset = atof(val);
	val = getenv("{tier_upper}_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY");
	if (val)
		g_lookahead_gac_global_min_entropy = atoi(val);
	val = getenv("{tier_upper}_LOOKAHEAD_CONSTR_LOCAL_MIN_UNSET");
	if (val)
		g_lookahead_constr_local_min_unset = atof(val);
	val = getenv("{tier_upper}_LOOKAHEAD_CONSTR_LOCAL_MAX_UNSET");
	if (val)
		g_lookahead_constr_local_max_unset = atof(val);
	val = getenv("{tier_upper}_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY");
	if (val)
		g_lookahead_constr_global_min_entropy = atoi(val);
	initialized = 1;
}}}}
#endif""",
        "target_init": """	rem = node->remaining_entropy;""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
	init_env();
#endif
	rem = node->remaining_entropy;"""
    })

FILES_CONFIGS = [
    ("src/prune_strat_routing.c", {
        "var_names": ["g_routing_shallow_ratio", "g_routing_medium_ratio"],
        "target_vars_template": """static const double	g_routing_shallow_ratio = {g_routing_shallow_ratio};
static const double	g_routing_medium_ratio = {g_routing_medium_ratio};""",
        "replacement_vars_template": """#include <stdlib.h>

static double	g_routing_shallow_ratio = {g_routing_shallow_ratio};
static double	g_routing_medium_ratio = {g_routing_medium_ratio};

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_routing_env(void)
{{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("ROUTING_SHALLOW_RATIO");
	if (val)
		g_routing_shallow_ratio = atof(val);
	val = getenv("ROUTING_MEDIUM_RATIO");
	if (val)
		g_routing_medium_ratio = atof(val);
	initialized = 1;
}}
#endif""",
        "target_init": """		d = puzzle->cur_node->cur_depth;
		scaling = 0.0;
		if (puzzle->size > 7)
			scaling = (puzzle->size - 7.0) * (puzzle->size - 7.0) / 4.0;
		if (d <= puzzle->squared_size * g_routing_shallow_ratio * scaling)""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
		init_routing_env();
#endif
		d = puzzle->cur_node->cur_depth;
		scaling = 0.0;
		if (puzzle->size > 7)
			scaling = (puzzle->size - 7.0) * (puzzle->size - 7.0) / 4.0;
		if (d <= puzzle->squared_size * g_routing_shallow_ratio * scaling)"""
    }),
    make_tier_config("root", "ROOT"),
    make_tier_config("shallow", "SHALLOW"),
    make_tier_config("medium", "MEDIUM"),
    make_tier_config("deep", "DEEP"),
    ("src/sel_strat_routing.c", {
        "var_names": [
            "g_sel_period_coef_sqrt", "g_sel_period_coef_inv"
        ],
        "target_vars_template": """static const double			g_sel_period_coef_sqrt = {g_sel_period_coef_sqrt};
static const double			g_sel_period_coef_inv = {g_sel_period_coef_inv};""",
        "replacement_vars_template": """#include <stdlib.h>

static double			g_sel_period_coef_sqrt = {g_sel_period_coef_sqrt};
static double			g_sel_period_coef_inv = {g_sel_period_coef_inv};

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_sel_env(void)
{{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("SEL_PERIOD_COEF_SQRT");
	if (val)
		g_sel_period_coef_sqrt = atof(val);
	val = getenv("SEL_PERIOD_COEF_INV");
	if (val)
		g_sel_period_coef_inv = atof(val);
	initialized = 1;
}}
#endif""",
        "target_init": """	rem = node->remaining_entropy;""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
	init_sel_env();
#endif
	rem = node->remaining_entropy;"""
    })
]

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply or unapply environment overrides to C++ files.")
    parser.add_argument("--unapply", action="store_true", help="Remove overrides and restore original static const configurations.")
    args = parser.parse_args()
    
    for filepath, config in FILES_CONFIGS:
        if not os.path.exists(filepath):
            print(f"Warning: file not found: {filepath}")
            continue
            
        with open(filepath, "r") as f:
            content = f.read()
            
        # Parse current values dynamically
        var_values = {}
        for var_name in config["var_names"]:
            pattern = re.compile(rf'static\s+(?:const\s+)?(?:double|int)\s+{var_name}\s*=\s*([^;]+);')
            match = pattern.search(content)
            if match:
                var_values[var_name] = match.group(1).strip()
            else:
                print(f"Error: Could not find parameter declaration for '{var_name}' in '{filepath}'", file=sys.stderr)
                sys.exit(1)
                
        # Format templates
        target_vars = config["target_vars_template"].format(**var_values)
        replacement_vars = config["replacement_vars_template"].format(**var_values)
        
        target_init = config["target_init"]
        replacement_init = config["replacement_init"]
        
        if args.unapply:
            # 1. Replace replacement_vars with target_vars
            if replacement_vars in content:
                content = content.replace(replacement_vars, target_vars)
            elif target_vars in content:
                pass # Already unapplied
            else:
                # Fallback: self-heal broken/partial states
                print(f"Warning: Block mismatch in {filepath}. Initiating individual var const restoration...")
                func_name = "init_routing_env" if "routing" in filepath else ("init_sel_env" if "sel" in filepath else "init_env")
                pattern_func = re.compile(rf'#if\s+!defined\(G_PRUNE_NO_ENV\).*?static\s+void\s+{func_name}\(void\).*?#endif', re.DOTALL)
                content = pattern_func.sub("", content)
                content = content.replace("#include <stdlib.h>\n\n", "")
                content = content.replace("#include <stdlib.h>\n", "")
                
                # Restore "const" declaration
                for var_name in config["var_names"]:
                    pattern_var = re.compile(rf'static\s+(double|int)(\s+){var_name}(\s*=)')
                    content = pattern_var.sub(rf'static const \1\2{var_name}\3', content)
            
            # 2. Replace replacement_init with target_init
            if replacement_init in content:
                content = content.replace(replacement_init, target_init)
                
            action_str = "Successfully unapplied overrides from"
        else:
            # 1. Replace target_vars with replacement_vars
            if target_vars in content:
                content = content.replace(target_vars, replacement_vars)
            elif replacement_vars in content:
                pass # Already applied
            else:
                print(f"Warning: Target block not found in {filepath}. Variables might be already modified or mismatched.")
                
            # 2. Replace target_init with replacement_init
            if target_init in content:
                content = content.replace(target_init, replacement_init)
                
            action_str = "Successfully applied overrides to"
            
        with open(filepath, "w") as f:
            f.write(content)
        print(f"{action_str} {filepath}")

if __name__ == "__main__":
    main()
