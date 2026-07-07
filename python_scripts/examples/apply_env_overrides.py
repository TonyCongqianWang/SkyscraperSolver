#!/usr/bin/env python3
import os
import sys
import re

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
		if (d <= puzzle->squared_size * g_routing_shallow_ratio)""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
		init_routing_env();
#endif
		d = puzzle->cur_node->cur_depth;
		if (d <= puzzle->squared_size * g_routing_shallow_ratio)"""
    }),
    ("src/prune_strat_root.c", {
        "var_names": [
            "g_gac_unset_threshold", "g_constr_min_unset", "g_constr_max_unset",
            "g_lookahead_gac_unset_threshold", "g_lookahead_constr_min_unset", "g_lookahead_constr_max_unset",
            "g_lookahead_downgrade_fraction",
            "g_period_base", "g_period_coef1", "g_period_coef2"
        ],
        "target_vars_template": """static const double	g_gac_unset_threshold = {g_gac_unset_threshold};
static const double	g_constr_min_unset = {g_constr_min_unset};
static const double	g_constr_max_unset = {g_constr_max_unset};
static const double	g_lookahead_gac_unset_threshold = {g_lookahead_gac_unset_threshold};
static const double	g_lookahead_constr_min_unset = {g_lookahead_constr_min_unset};
static const double	g_lookahead_constr_max_unset = {g_lookahead_constr_max_unset};
static const double	g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static const int	g_period_base = {g_period_base};
static const int	g_period_coef1 = {g_period_coef1};
static const int	g_period_coef2 = {g_period_coef2};""",
        "replacement_vars_template": """#include <stdlib.h>

static double	g_gac_unset_threshold = {g_gac_unset_threshold};
static double	g_constr_min_unset = {g_constr_min_unset};
static double	g_constr_max_unset = {g_constr_max_unset};
static double	g_lookahead_gac_unset_threshold = {g_lookahead_gac_unset_threshold};
static double	g_lookahead_constr_min_unset = {g_lookahead_constr_min_unset};
static double	g_lookahead_constr_max_unset = {g_lookahead_constr_max_unset};
static double	g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static int		g_period_base = {g_period_base};
static int		g_period_coef1 = {g_period_coef1};
static int		g_period_coef2 = {g_period_coef2};

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("ROOT_GAC_UNSET_THRESHOLD");
	if (val)
		g_gac_unset_threshold = atof(val);
	val = getenv("ROOT_CONSTR_MIN_UNSET");
	if (val)
		g_constr_min_unset = atof(val);
	val = getenv("ROOT_CONSTR_MAX_UNSET");
	if (val)
		g_constr_max_unset = atof(val);
	val = getenv("ROOT_LOOKAHEAD_GAC_UNSET_THRESHOLD");
	if (val)
		g_lookahead_gac_unset_threshold = atof(val);
	val = getenv("ROOT_LOOKAHEAD_CONSTR_MIN_UNSET");
	if (val)
		g_lookahead_constr_min_unset = atof(val);
	val = getenv("ROOT_LOOKAHEAD_CONSTR_MAX_UNSET");
	if (val)
		g_lookahead_constr_max_unset = atof(val);
	val = getenv("ROOT_LOOKAHEAD_DOWNGRADE_FRACTION");
	if (val)
		g_lookahead_downgrade_fraction = atof(val);
	val = getenv("ROOT_PERIOD_BASE");
	if (val)
		g_period_base = atoi(val);
	val = getenv("ROOT_PERIOD_COEF1");
	if (val)
		g_period_coef1 = atoi(val);
	val = getenv("ROOT_PERIOD_COEF2");
	if (val)
		g_period_coef2 = atoi(val);
	initialized = 1;
}}
#endif""",
        "target_init": """	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
	init_env();
#endif
	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);"""
    }),
    ("src/prune_strat_shallow.c", {
        "var_names": [
            "g_min_unset_threshold", "g_gac_unset_threshold", "g_constr_min_unset", "g_constr_max_unset",
            "g_lookahead_gac_unset_threshold", "g_lookahead_constr_min_unset", "g_lookahead_constr_max_unset",
            "g_lookahead_downgrade_fraction",
            "g_period_base", "g_period_coef1", "g_period_coef2"
        ],
        "target_vars_template": """static const double	g_min_unset_threshold = {g_min_unset_threshold};
static const double	g_gac_unset_threshold = {g_gac_unset_threshold};
static const double	g_constr_min_unset = {g_constr_min_unset};
static const double	g_constr_max_unset = {g_constr_max_unset};
static const double	g_lookahead_gac_unset_threshold = {g_lookahead_gac_unset_threshold};
static const double	g_lookahead_constr_min_unset = {g_lookahead_constr_min_unset};
static const double	g_lookahead_constr_max_unset = {g_lookahead_constr_max_unset};
static const double	g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static const int	g_period_base = {g_period_base};
static const int	g_period_coef1 = {g_period_coef1};
static const int	g_period_coef2 = {g_period_coef2};""",
        "replacement_vars_template": """#include <stdlib.h>

static double	g_min_unset_threshold = {g_min_unset_threshold};
static double	g_gac_unset_threshold = {g_gac_unset_threshold};
static double	g_constr_min_unset = {g_constr_min_unset};
static double	g_constr_max_unset = {g_constr_max_unset};
static double	g_lookahead_gac_unset_threshold = {g_lookahead_gac_unset_threshold};
static double	g_lookahead_constr_min_unset = {g_lookahead_constr_min_unset};
static double	g_lookahead_constr_max_unset = {g_lookahead_constr_max_unset};
static double	g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static int		g_period_base = {g_period_base};
static int		g_period_coef1 = {g_period_coef1};
static int		g_period_coef2 = {g_period_coef2};

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("SHALLOW_MIN_UNSET");
	if (val)
		g_min_unset_threshold = atof(val);
	val = getenv("SHALLOW_GAC_UNSET_THRESHOLD");
	if (val)
		g_gac_unset_threshold = atof(val);
	val = getenv("SHALLOW_CONSTR_MIN_UNSET");
	if (val)
		g_constr_min_unset = atof(val);
	val = getenv("SHALLOW_CONSTR_MAX_UNSET");
	if (val)
		g_constr_max_unset = atof(val);
	val = getenv("SHALLOW_LOOKAHEAD_GAC_UNSET_THRESHOLD");
	if (val)
		g_lookahead_gac_unset_threshold = atof(val);
	val = getenv("SHALLOW_LOOKAHEAD_CONSTR_MIN_UNSET");
	if (val)
		g_lookahead_constr_min_unset = atof(val);
	val = getenv("SHALLOW_LOOKAHEAD_CONSTR_MAX_UNSET");
	if (val)
		g_lookahead_constr_max_unset = atof(val);
	val = getenv("SHALLOW_LOOKAHEAD_DOWNGRADE_FRACTION");
	if (val)
		g_lookahead_downgrade_fraction = atof(val);
	val = getenv("SHALLOW_PERIOD_BASE");
	if (val)
		g_period_base = atoi(val);
	val = getenv("SHALLOW_PERIOD_COEF1");
	if (val)
		g_period_coef1 = atoi(val);
	val = getenv("SHALLOW_PERIOD_COEF2");
	if (val)
		g_period_coef2 = atoi(val);
	initialized = 1;
}}
#endif""",
        "target_init": """	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
	init_env();
#endif
	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);"""
    }),
    ("src/prune_strat_medium.c", {
        "var_names": [
            "g_min_unset_threshold", "g_gac_unset_threshold", "g_constr_min_unset", "g_constr_max_unset",
            "g_lookahead_gac_unset_threshold", "g_lookahead_constr_min_unset", "g_lookahead_constr_max_unset",
            "g_lookahead_downgrade_fraction",
            "g_period_base", "g_period_coef1", "g_period_coef2"
        ],
        "target_vars_template": """static const double	g_min_unset_threshold = {g_min_unset_threshold};
static const double	g_gac_unset_threshold = {g_gac_unset_threshold};
static const double	g_constr_min_unset = {g_constr_min_unset};
static const double	g_constr_max_unset = {g_constr_max_unset};
static const double	g_lookahead_gac_unset_threshold = {g_lookahead_gac_unset_threshold};
static const double	g_lookahead_constr_min_unset = {g_lookahead_constr_min_unset};
static const double	g_lookahead_constr_max_unset = {g_lookahead_constr_max_unset};
static const double	g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static const int	g_period_base = {g_period_base};
static const int	g_period_coef1 = {g_period_coef1};
static const int	g_period_coef2 = {g_period_coef2};""",
        "replacement_vars_template": """#include <stdlib.h>

static double	g_min_unset_threshold = {g_min_unset_threshold};
static double	g_gac_unset_threshold = {g_gac_unset_threshold};
static double	g_constr_min_unset = {g_constr_min_unset};
static double	g_constr_max_unset = {g_constr_max_unset};
static double	g_lookahead_gac_unset_threshold = {g_lookahead_gac_unset_threshold};
static double	g_lookahead_constr_min_unset = {g_lookahead_constr_min_unset};
static double	g_lookahead_constr_max_unset = {g_lookahead_constr_max_unset};
static double	g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static int		g_period_base = {g_period_base};
static int		g_period_coef1 = {g_period_coef1};
static int		g_period_coef2 = {g_period_coef2};

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("MEDIUM_MIN_UNSET");
	if (val)
		g_min_unset_threshold = atof(val);
	val = getenv("MEDIUM_GAC_UNSET_THRESHOLD");
	if (val)
		g_gac_unset_threshold = atof(val);
	val = getenv("MEDIUM_CONSTR_MIN_UNSET");
	if (val)
		g_constr_min_unset = atof(val);
	val = getenv("MEDIUM_CONSTR_MAX_UNSET");
	if (val)
		g_constr_max_unset = atof(val);
	val = getenv("MEDIUM_LOOKAHEAD_GAC_UNSET_THRESHOLD");
	if (val)
		g_lookahead_gac_unset_threshold = atof(val);
	val = getenv("MEDIUM_LOOKAHEAD_CONSTR_MIN_UNSET");
	if (val)
		g_lookahead_constr_min_unset = atof(val);
	val = getenv("MEDIUM_LOOKAHEAD_CONSTR_MAX_UNSET");
	if (val)
		g_lookahead_constr_max_unset = atof(val);
	val = getenv("MEDIUM_LOOKAHEAD_DOWNGRADE_FRACTION");
	if (val)
		g_lookahead_downgrade_fraction = atof(val);
	val = getenv("MEDIUM_PERIOD_BASE");
	if (val)
		g_period_base = atoi(val);
	val = getenv("MEDIUM_PERIOD_COEF1");
	if (val)
		g_period_coef1 = atoi(val);
	val = getenv("MEDIUM_PERIOD_COEF2");
	if (val)
		g_period_coef2 = atoi(val);
	initialized = 1;
}}
#endif""",
        "target_init": """	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
	init_env();
#endif
	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);"""
    }),
    ("src/prune_strat_deep.c", {
        "var_names": [
            "g_min_unset_threshold", "g_gac_unset_threshold", "g_constr_min_unset", "g_constr_max_unset",
            "g_lookahead_gac_unset_threshold", "g_lookahead_constr_min_unset", "g_lookahead_constr_max_unset",
            "g_lookahead_downgrade_fraction",
            "g_period_base", "g_period_coef1", "g_period_coef2"
        ],
        "target_vars_template": """static const double	g_min_unset_threshold = {g_min_unset_threshold};
static const double	g_gac_unset_threshold = {g_gac_unset_threshold};
static const double	g_constr_min_unset = {g_constr_min_unset};
static const double	g_constr_max_unset = {g_constr_max_unset};
static const double	g_lookahead_gac_unset_threshold = {g_lookahead_gac_unset_threshold};
static const double	g_lookahead_constr_min_unset = {g_lookahead_constr_min_unset};
static const double	g_lookahead_constr_max_unset = {g_lookahead_constr_max_unset};
static const double	g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static const int	g_period_base = {g_period_base};
static const int	g_period_coef1 = {g_period_coef1};
static const int	g_period_coef2 = {g_period_coef2};""",
        "replacement_vars_template": """#include <stdlib.h>

static double	g_min_unset_threshold = {g_min_unset_threshold};
static double	g_gac_unset_threshold = {g_gac_unset_threshold};
static double	g_constr_min_unset = {g_constr_min_unset};
static double	g_constr_max_unset = {g_constr_max_unset};
static double	g_lookahead_gac_unset_threshold = {g_lookahead_gac_unset_threshold};
static double	g_lookahead_constr_min_unset = {g_lookahead_constr_min_unset};
static double	g_lookahead_constr_max_unset = {g_lookahead_constr_max_unset};
static double	g_lookahead_downgrade_fraction = {g_lookahead_downgrade_fraction};
static int		g_period_base = {g_period_base};
static int		g_period_coef1 = {g_period_coef1};
static int		g_period_coef2 = {g_period_coef2};

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("DEEP_MIN_UNSET");
	if (val)
		g_min_unset_threshold = atof(val);
	val = getenv("DEEP_GAC_UNSET_THRESHOLD");
	if (val)
		g_gac_unset_threshold = atof(val);
	val = getenv("DEEP_CONSTR_MIN_UNSET");
	if (val)
		g_constr_min_unset = atof(val);
	val = getenv("DEEP_CONSTR_MAX_UNSET");
	if (val)
		g_constr_max_unset = atof(val);
	val = getenv("DEEP_LOOKAHEAD_GAC_UNSET_THRESHOLD");
	if (val)
		g_lookahead_gac_unset_threshold = atof(val);
	val = getenv("DEEP_LOOKAHEAD_CONSTR_MIN_UNSET");
	if (val)
		g_lookahead_constr_min_unset = atof(val);
	val = getenv("DEEP_LOOKAHEAD_CONSTR_MAX_UNSET");
	if (val)
		g_lookahead_constr_max_unset = atof(val);
	val = getenv("DEEP_LOOKAHEAD_DOWNGRADE_FRACTION");
	if (val)
		g_lookahead_downgrade_fraction = atof(val);
	val = getenv("DEEP_PERIOD_BASE");
	if (val)
		g_period_base = atoi(val);
	val = getenv("DEEP_PERIOD_COEF1");
	if (val)
		g_period_coef1 = atoi(val);
	val = getenv("DEEP_PERIOD_COEF2");
	if (val)
		g_period_coef2 = atoi(val);
	initialized = 1;
}}
#endif""",
        "target_init": """	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
	init_env();
#endif
	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);"""
    }),
    ("src/sel_strat_routing.c", {
        "var_names": ["g_sel_rebuild_period", "g_sel_ord2_coeff", "g_sel_ord4_coeff"],
        "target_vars_template": """static const double			g_sel_rebuild_period = {g_sel_rebuild_period};
static const double			g_sel_ord2_coeff = {g_sel_ord2_coeff};
static const double			g_sel_ord4_coeff = {g_sel_ord4_coeff};""",
        "replacement_vars_template": """#include <stdlib.h>

static double			g_sel_rebuild_period = {g_sel_rebuild_period};
static double			g_sel_ord2_coeff = {g_sel_ord2_coeff};
static double			g_sel_ord4_coeff = {g_sel_ord4_coeff};

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_sel_env(void)
{{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("SEL_REBUILD_PERIOD");
	if (val)
		g_sel_rebuild_period = atof(val);
	val = getenv("SEL_ORD2_COEFF");
	if (val)
		g_sel_ord2_coeff = atof(val);
	val = getenv("SEL_ORD4_COEFF");
	if (val)
		g_sel_ord4_coeff = atof(val);
	initialized = 1;
}}
#endif""",
        "target_init": """	node = puzzle->cur_node;
	config->score_family = SCORE_BRANCHING;""",
        "replacement_init": """#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
	init_sel_env();
#endif
	node = puzzle->cur_node;
	config->score_family = SCORE_BRANCHING;"""
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
