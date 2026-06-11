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

#ifndef G_MIN_UNSET_R_PRUNE
# define G_MIN_UNSET_R_PRUNE 0.5
#endif

#ifndef G_PRUNE_PERIOD_SHALLOW
# define G_PRUNE_PERIOD_SHALLOW 120
#endif

#ifndef G_PRUNE_EXTRA_PERIOD_DEEP
# define G_PRUNE_EXTRA_PERIOD_DEEP 150
#endif

#ifndef G_PRUNE_DEPTH_THRESHOLD_0
# define G_PRUNE_DEPTH_THRESHOLD_0 0
#endif

#ifndef G_PRUNE_DEPTH_THRESHOLD_1
# define G_PRUNE_DEPTH_THRESHOLD_1 3
#endif

#ifndef G_PRUNE_DISABLE_GAC
# define G_PRUNE_DISABLE_GAC 0
#endif

#ifndef G_PRUNE_LOOKAHEAD_PRUNING_LEVEL
# define G_PRUNE_LOOKAHEAD_PRUNING_LEVEL 1
#endif

static const double			g_min_unset_r_prune
	= G_MIN_UNSET_R_PRUNE;
static const t_prune_prog	g_prune_period_shallow
	= G_PRUNE_PERIOD_SHALLOW;
static const t_prune_prog	g_prune_extra_period_deep
	= G_PRUNE_EXTRA_PERIOD_DEEP;
static const int			g_prune_depth_threshold_0
	= G_PRUNE_DEPTH_THRESHOLD_0;
static const int			g_prune_depth_threshold_1
	= G_PRUNE_DEPTH_THRESHOLD_1;
static const int			g_prune_disable_gac
	= G_PRUNE_DISABLE_GAC;
static const int			g_prune_lookahead_pruning_level
	= G_PRUNE_LOOKAHEAD_PRUNING_LEVEL;

static int	should_skip_prune(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			unset_ratio;
	t_prune_prog	period;

	node = puzzle->cur_node;
	if (node->num_unset == 0)
		return (1);
	if (node->progress_counter == 0)
		return (0);
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	period = g_prune_period_shallow;
	if (node->cur_depth > g_prune_depth_threshold_0)
		period += g_prune_extra_period_deep;
	if (node->cur_depth > g_prune_depth_threshold_1)
		period += g_prune_extra_period_deep;
	period = (t_prune_prog)(period / unset_ratio);
	return (node->progress_counter < node->last_prune_prog + period);
}

static void	set_root_prune(t_prune_config *config)
{
	if (g_prune_disable_gac)
		config->strategy = PRUNE_LOOKAHEAD_DIVE;
	else
		config->strategy = PRUNE_HYBRID;
	config->lookahead.is_selective = 0;
	config->lookahead.max_depth = 1;
	config->lookahead.branching_budget = 0;
	config->lookahead.enable_node_select = 0;
	config->lookahead.pruning_level = g_prune_lookahead_pruning_level;
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
	config->lookahead.pruning_level = g_prune_lookahead_pruning_level;
	if (!g_prune_disable_gac && unset_ratio > 0.7)
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
