#!/usr/bin/env python3
import os

FILES_CONFIGS = [
    ("src/prune_strat_routing.c", {
        "target_vars": """static const double	g_routing_shallow_ratio = 0.05008353583779075;
static const double	g_routing_medium_ratio = 0.2736100962866644;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_routing_shallow_ratio = 0.05008353583779075;
static double	g_routing_medium_ratio = 0.2736100962866644;

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
        "target_vars": """static const double	g_gac_unset_threshold = 0.4634853676455628;
static const double	g_constr_min_unset = 0.820455247534949;
static const double	g_constr_max_unset = 0.33143801544130486;
static const int	g_period_base = 70;
static const int	g_period_coef1 = 1855;
static const int	g_period_coef2 = 109817;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_gac_unset_threshold = 0.4634853676455628;
static double	g_constr_min_unset = 0.820455247534949;
static double	g_constr_max_unset = 0.33143801544130486;
static int		g_period_base = 70;
static int		g_period_coef1 = 1855;
static int		g_period_coef2 = 109817;

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
        "target_vars": """static const double	g_min_unset_threshold = 0.41167205890726744;
static const double	g_gac_unset_threshold = 0.628986930862801;
static const double	g_constr_min_unset = 0.49682108776980893;
static const double	g_constr_max_unset = 0.9425750932165332;
static const int	g_period_base = 39;
static const int	g_period_coef1 = 1683;
static const int	g_period_coef2 = 11533;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_min_unset_threshold = 0.41167205890726744;
static double	g_gac_unset_threshold = 0.628986930862801;
static double	g_constr_min_unset = 0.49682108776980893;
static double	g_constr_max_unset = 0.9425750932165332;
static int		g_period_base = 39;
static int		g_period_coef1 = 1683;
static int		g_period_coef2 = 11533;

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
        "target_vars": """static const double	g_min_unset_threshold = 0.38779700452737015;
static const double	g_gac_unset_threshold = 0.19090341649850168;
static const double	g_constr_min_unset = 0.9771216210974851;
static const double	g_constr_max_unset = 0.8502859539542834;
static const int	g_period_base = 104;
static const int	g_period_coef1 = 2579;
static const int	g_period_coef2 = 135680;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_min_unset_threshold = 0.38779700452737015;
static double	g_gac_unset_threshold = 0.19090341649850168;
static double	g_constr_min_unset = 0.9771216210974851;
static double	g_constr_max_unset = 0.8502859539542834;
static int		g_period_base = 104;
static int		g_period_coef1 = 2579;
static int		g_period_coef2 = 135680;

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
        "target_vars": """static const double	g_min_unset_threshold = 0.04487051200407117;
static const double	g_gac_unset_threshold = 0.2938803129321176;
static const double	g_constr_min_unset = 1.0;
static const double	g_constr_max_unset = 0.42472576251042726;
static const int	g_period_base = 230;
static const int	g_period_coef1 = 11401;
static const int	g_period_coef2 = 116580;""",
        "replacement_vars": """#include <stdlib.h>

static double	g_min_unset_threshold = 0.04487051200407117;
static double	g_gac_unset_threshold = 0.2938803129321176;
static double	g_constr_min_unset = 1.0;
static double	g_constr_max_unset = 0.42472576251042726;
static int		g_period_base = 230;
static int		g_period_coef1 = 11401;
static int		g_period_coef2 = 116580;

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
    })
]

def main():
    for filepath, config in FILES_CONFIGS:
        with open(filepath, "r") as f:
            content = f.read()
        
        # Replace variables
        if config["target_vars"] in content:
            content = content.replace(config["target_vars"], config["replacement_vars"])
        else:
            print(f"Warning: target_vars not found in {filepath}")
            
        # Replace check threshold if configured
        if "target_check" in config:
            if config["target_check"] in content:
                content = content.replace(config["target_check"], config["replacement_check"])
            else:
                print(f"Warning: target_check not found in {filepath}")
                
        # Replace init call
        if config["target_init"] in content:
            content = content.replace(config["target_init"], config["replacement_init"])
        else:
            print(f"Warning: target_init not found in {filepath}")
            
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Successfully applied overrides to {filepath}")

if __name__ == "__main__":
    main()
