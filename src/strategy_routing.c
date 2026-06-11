/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   strategy_routing.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "strategy_routing.h"

#ifndef G_MIN_UNSET_R_PRUNE
# define G_MIN_UNSET_R_PRUNE		0.4
#endif
#ifndef G_PRUNE_PERIOD_SHALLOW
# define G_PRUNE_PERIOD_SHALLOW		16
#endif
#ifndef G_PRUNE_EXTRA_PERIOD_DEEP
# define G_PRUNE_EXTRA_PERIOD_DEEP	15
#endif
#ifndef REBUILD_PERIOD
# define REBUILD_PERIOD			16
#endif

#define G_DEPTH_THRESHOLD_0		0
#define G_DEPTH_THRESHOLD_1		3

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
	period = G_PRUNE_PERIOD_SHALLOW;
	if (node->cur_depth > G_DEPTH_THRESHOLD_0)
		period += G_PRUNE_EXTRA_PERIOD_DEEP;
	if (node->cur_depth > G_DEPTH_THRESHOLD_1)
		period += G_PRUNE_EXTRA_PERIOD_DEEP;
	period = (t_prune_prog)(period / unset_ratio);
	period *= 10;
	return (node->progress_counter < node->last_prune_prog + period);
}

#ifndef G_LOOKAHEAD_PRUNING_LEVEL
# define G_LOOKAHEAD_PRUNING_LEVEL	1
#endif

#ifndef DISABLE_GAC
# define DISABLE_GAC 0
#endif

static void	set_root_prune(t_prune_config *config)
{
	if (DISABLE_GAC)
		config->strategy = PRUNE_LOOKAHEAD_DIVE;
	else
		config->strategy = PRUNE_HYBRID;
	config->lookahead.is_selective = 0;
	config->lookahead.max_depth = 1;
	config->lookahead.branching_budget = 0;
	config->lookahead.enable_node_select = 0;
	config->lookahead.pruning_level = G_LOOKAHEAD_PRUNING_LEVEL;
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
	config->lookahead.pruning_level = G_LOOKAHEAD_PRUNING_LEVEL;
	if (!DISABLE_GAC && unset_ratio > 0.7)
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
	if (unset_ratio < G_MIN_UNSET_R_PRUNE)
	{
		config->strategy = PRUNE_NONE;
		return ;
	}
	if (puzzle->cur_node->cur_depth == 0)
		set_root_prune(config);
	else
		set_deep_prune(config, unset_ratio);
}

void	select_node_select_config(t_puzzle *puzzle,
			t_node_select_config *config)
{
	t_node_state	*node;
	double			unset_ratio;
	t_prune_prog	period;

	node = puzzle->cur_node;
	config->score_family = SCORE_BRANCHING;
	config->criterion = SELECT_MAX;
	config->enable_cache = 1;
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	period = REBUILD_PERIOD;
	if (node->cur_depth > G_DEPTH_THRESHOLD_0)
		period += G_PRUNE_EXTRA_PERIOD_DEEP;
	if (node->cur_depth > G_DEPTH_THRESHOLD_1)
		period += G_PRUNE_EXTRA_PERIOD_DEEP;
	if (unset_ratio > 0.0)
		period = (t_prune_prog)(period / unset_ratio);
	else
		period = 99999999;
	period *= 10;
	config->rebuild_period = period;
	config->start_cell_idx = -1;
	config->start_cell_val = 1;
	config->is_selective = 0;
}
