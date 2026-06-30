#!/usr/bin/env python3
import os

FILES_CONFIGS = [
    ("src/prune_strat_routing.c", {
        "target_vars": """static const double	g_routing_shallow_ratio = 0.05;
static const double	g_routing_medium_ratio = 0.33;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_routing_shallow_ratio = 0.05;
static double	g_routing_medium_ratio = 0.33;

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_routing_env(void)
{
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
}
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
        "target_vars": """static const double	g_gac_unset_threshold = 0.12;
static const double	g_constr_min_unset = 0.05;
static const double	g_constr_max_unset = 0.92;
static const int	g_period_base = 6;
static const int	g_period_coef1 = 900;
static const int	g_period_coef2 = 10000;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_gac_unset_threshold = 0.12;
static double	g_constr_min_unset = 0.05;
static double	g_constr_max_unset = 0.92;
static int		g_period_base = 6;
static int		g_period_coef1 = 900;
static int		g_period_coef2 = 10000;

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{
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
}
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
        "target_vars": """static const double	g_min_unset_threshold = 0.45;
static const double	g_gac_unset_threshold = 0.13;
static const double	g_constr_min_unset = 0.45;
static const double	g_constr_max_unset = 0.78;
static const int	g_period_base = 4;
static const int	g_period_coef1 = 2500;
static const int	g_period_coef2 = 25000;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_min_unset_threshold = 0.45;
static double	g_gac_unset_threshold = 0.13;
static double	g_constr_min_unset = 0.45;
static double	g_constr_max_unset = 0.78;
static int		g_period_base = 4;
static int		g_period_coef1 = 2500;
static int		g_period_coef2 = 25000;

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{
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
}
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
        "target_vars": """static const double	g_min_unset_threshold = 0.35;
static const double	g_gac_unset_threshold = 0.16;
static const double	g_constr_min_unset = 0.40;
static const double	g_constr_max_unset = 0.76;
static const int	g_period_base = 65;
static const int	g_period_coef1 = 6000;
static const int	g_period_coef2 = 100000;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_min_unset_threshold = 0.35;
static double	g_gac_unset_threshold = 0.16;
static double	g_constr_min_unset = 0.40;
static double	g_constr_max_unset = 0.76;
static int		g_period_base = 65;
static int		g_period_coef1 = 6000;
static int		g_period_coef2 = 100000;

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{
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
}
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
        "target_vars": """static const double	g_min_unset_threshold = 0.09;
static const double	g_gac_unset_threshold = 0.22;
static const double	g_constr_min_unset = 0.49;
static const double	g_constr_max_unset = 0.57;
static const int	g_period_base = 240;
static const int	g_period_coef1 = 12500;
static const int	g_period_coef2 = 100000;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_min_unset_threshold = 0.09;
static double	g_gac_unset_threshold = 0.22;
static double	g_constr_min_unset = 0.49;
static double	g_constr_max_unset = 0.57;
static int		g_period_base = 240;
static int		g_period_coef1 = 12500;
static int		g_period_coef2 = 100000;

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{
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
}
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
        "target_vars": """static const double			g_sel_rebuild_period = 1000;
static const double			g_sel_ord2_coeff = 2500;
static const double			g_sel_ord4_coeff = 80000;""",
        "replacement_vars": """#include <stdlib.h>

static double			g_sel_rebuild_period = 1000;
static double			g_sel_ord2_coeff = 2500;
static double			g_sel_ord4_coeff = 80000;

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_sel_env(void)
{
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
}
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
            
        if args.unapply:
            # Unapply variables
            if config["replacement_vars"] in content:
                content = content.replace(config["replacement_vars"], config["target_vars"])
            else:
                print(f"Warning: replacement_vars not found in {filepath} (already unapplied?)")
                
            # Unapply check threshold if configured
            if "replacement_check" in config:
                if config["replacement_check"] in content:
                    content = content.replace(config["replacement_check"], config["target_check"])
                else:
                    print(f"Warning: replacement_check not found in {filepath}")
                    
            # Unapply init call
            if config["replacement_init"] in content:
                content = content.replace(config["replacement_init"], config["target_init"])
            else:
                print(f"Warning: replacement_init not found in {filepath}")
                
            action_str = "Successfully unapplied overrides from"
        else:
            # Apply variables
            if config["target_vars"] in content:
                content = content.replace(config["target_vars"], config["replacement_vars"])
            else:
                print(f"Warning: target_vars not found in {filepath} (already applied?)")
                
            # Apply check threshold if configured
            if "target_check" in config:
                if config["target_check"] in content:
                    content = content.replace(config["target_check"], config["replacement_check"])
                else:
                    print(f"Warning: target_check not found in {filepath}")
                    
            # Apply init call
            if config["target_init"] in content:
                content = content.replace(config["target_init"], config["replacement_init"])
            else:
                print(f"Warning: target_init not found in {filepath}")
                
            action_str = "Successfully applied overrides to"
            
        with open(filepath, "w") as f:
            f.write(content)
        print(f"{action_str} {filepath}")

if __name__ == "__main__":
    main()
