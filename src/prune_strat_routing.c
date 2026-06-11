/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_routing.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 14:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 14:20:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "strategy_routing.h"

#ifndef G_PRUNE_NO_ENV
# define G_PRUNE_NO_ENV 1
#endif

#ifndef G_MIN_UNSET_R_PRUNE
# define G_MIN_UNSET_R_PRUNE 0.5
#endif

#ifndef G_PRUNE_PERIOD_SHALLOW
# define G_PRUNE_PERIOD_SHALLOW 240
#endif

#ifndef G_PRUNE_EXTRA_PERIOD_DEEP
# define G_PRUNE_EXTRA_PERIOD_DEEP 200
#endif

#ifndef G_PRUNE_DEPTH_THRESHOLD_0
# define G_PRUNE_DEPTH_THRESHOLD_0 1
#endif

#ifndef G_PRUNE_DEPTH_THRESHOLD_1
# define G_PRUNE_DEPTH_THRESHOLD_1 4
#endif

#ifndef G_PRUNE_GAC_UNSET_R_THRESHOLD
# define G_PRUNE_GAC_UNSET_R_THRESHOLD 0.6
#endif

#ifndef G_PRUNE_LIN_COEFF
# define G_PRUNE_LIN_COEFF 0.1
#endif

#ifndef G_PRUNE_QUAD_COEFF
# define G_PRUNE_QUAD_COEFF 1.5
#endif

#ifndef G_PRUNE_CUBIC_COEFF
# define G_PRUNE_CUBIC_COEFF 0.0
#endif

#ifndef G_PRUNE_NO_ENV
# include <stdlib.h>
#endif

#ifndef G_PRUNE_NO_ENV
static double			g_min_unset_r_prune = G_MIN_UNSET_R_PRUNE;
static t_prune_prog		g_prune_period_shallow = G_PRUNE_PERIOD_SHALLOW;
static t_prune_prog		g_prune_extra_period_deep = G_PRUNE_EXTRA_PERIOD_DEEP;
static int				g_prune_depth_threshold_0 = G_PRUNE_DEPTH_THRESHOLD_0;
static int				g_prune_depth_threshold_1 = G_PRUNE_DEPTH_THRESHOLD_1;
static double			g_prune_gac_unset_r_threshold = G_PRUNE_GAC_UNSET_R_THRESHOLD;
static double			g_prune_lin_coeff = G_PRUNE_LIN_COEFF;
static double			g_prune_quad_coeff = G_PRUNE_QUAD_COEFF;
static double			g_prune_cubic_coeff = G_PRUNE_CUBIC_COEFF;
int						g_keep_pruning = 0;
#else
static const double			g_min_unset_r_prune = G_MIN_UNSET_R_PRUNE;
static const t_prune_prog	g_prune_period_shallow = G_PRUNE_PERIOD_SHALLOW;
static const t_prune_prog	g_prune_extra_period_deep = G_PRUNE_EXTRA_PERIOD_DEEP;
static const int			g_prune_depth_threshold_0 = G_PRUNE_DEPTH_THRESHOLD_0;
static const int			g_prune_depth_threshold_1 = G_PRUNE_DEPTH_THRESHOLD_1;
static const double			g_prune_gac_unset_r_threshold = G_PRUNE_GAC_UNSET_R_THRESHOLD;
static const double			g_prune_lin_coeff = G_PRUNE_LIN_COEFF;
static const double			g_prune_quad_coeff = G_PRUNE_QUAD_COEFF;
static const double			g_prune_cubic_coeff = G_PRUNE_CUBIC_COEFF;
int							g_keep_pruning = 0;
#endif

#ifndef G_PRUNE_NO_ENV
__attribute__((constructor))
static void	init_pruning_env(void)
{
	char	*val;

	val = getenv("G_MIN_UNSET_R_PRUNE");
	if (val)
		g_min_unset_r_prune = atof(val);
	val = getenv("G_PRUNE_PERIOD_SHALLOW");
	if (val)
		g_prune_period_shallow = atoi(val);
	val = getenv("G_PRUNE_EXTRA_PERIOD_DEEP");
	if (val)
		g_prune_extra_period_deep = atoi(val);
	val = getenv("G_PRUNE_DEPTH_THRESHOLD_0");
	if (val)
		g_prune_depth_threshold_0 = atoi(val);
	val = getenv("G_PRUNE_DEPTH_THRESHOLD_1");
	if (val)
		g_prune_depth_threshold_1 = atoi(val);
	val = getenv("G_PRUNE_GAC_UNSET_R_THRESHOLD");
	if (val)
		g_prune_gac_unset_r_threshold = atof(val);
	val = getenv("G_PRUNE_LIN_COEFF");
	if (val)
		g_prune_lin_coeff = atof(val);
	val = getenv("G_PRUNE_QUAD_COEFF");
	if (val)
		g_prune_quad_coeff = atof(val);
	val = getenv("G_PRUNE_CUBIC_COEFF");
	if (val)
		g_prune_cubic_coeff = atof(val);
	val = getenv("KEEP_PRUNING");
	if (val)
		g_keep_pruning = atoi(val);
}
#endif

static int	should_skip_prune(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			unset_ratio;
	double			x;
	double			p;

	node = puzzle->cur_node;
	if (node->num_unset == 0)
		return (1);
	if (node->progress_counter == 0)
		return (0);
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	x = 1.0 - unset_ratio;
	p = g_prune_period_shallow;
	if (node->cur_depth > g_prune_depth_threshold_0)
		p += g_prune_extra_period_deep;
	if (node->cur_depth > g_prune_depth_threshold_1)
		p += g_prune_extra_period_deep;
	p *= (1.0 + g_prune_lin_coeff * x + g_prune_quad_coeff * x * x
			+ g_prune_cubic_coeff * x * x * x);
	return (node->progress_counter < node->last_prune_prog + (t_prune_prog)p);
}

static void	set_root_prune(t_prune_config *config)
{
	config->strategy = PRUNE_HYBRID;
	config->lookahead.is_selective = 0;
	config->lookahead.max_depth = 1;
	config->lookahead.branching_budget = 0;
	config->lookahead.enable_node_select = 0;
	config->lookahead.pruning_level = 1;
	config->gac.is_selective = 0;
	config->gac.max_k = 3;
	config->gac.analyse_naked = 1;
	config->gac.analyse_hidden = 1;
}

static void	set_deep_prune(t_prune_config *config, double unset_ratio)
{
	config->lookahead.is_selective = 1;
	config->lookahead.max_depth = 1;
	config->lookahead.branching_budget = 0;
	config->lookahead.enable_node_select = 0;
	config->lookahead.pruning_level = 1;
	if (unset_ratio > g_prune_gac_unset_r_threshold)
	{
		config->strategy = PRUNE_HYBRID;
		config->gac.is_selective = 1;
		config->gac.max_k = 2;
		config->gac.analyse_naked = 1;
		config->gac.analyse_hidden = 1;
	}
	else
	{
		config->strategy = PRUNE_LOOKAHEAD_DIVE;
	}
}

void	select_prune_config(t_puzzle *puzzle, t_prune_config *config)
{
	double	unset_ratio;

	if (should_skip_prune(puzzle))
	{
		config->strategy = PRUNE_NONE;
		return ;
	}
	unset_ratio = (double)puzzle->cur_node->num_unset / puzzle->squared_size;
	if (unset_ratio < g_min_unset_r_prune)
	{
		config->strategy = PRUNE_NONE;
		return ;
	}
	if (puzzle->cur_node->cur_depth == 0)
		set_root_prune(config);
	else
		set_deep_prune(config, unset_ratio);
}
