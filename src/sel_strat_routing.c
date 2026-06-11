/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sel_strat_routing.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 14:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 14:20:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "strategy_routing.h"

#ifndef G_SEL_REBUILD_PERIOD
# define G_SEL_REBUILD_PERIOD 2
#endif

#ifndef G_SEL_EXTRA_PERIOD_DEEP
# define G_SEL_EXTRA_PERIOD_DEEP 150
#endif

#ifndef G_SEL_DEPTH_THRESHOLD_0
# define G_SEL_DEPTH_THRESHOLD_0 0
#endif

#ifndef G_SEL_DEPTH_THRESHOLD_1
# define G_SEL_DEPTH_THRESHOLD_1 3
#endif

static const t_prune_prog	g_sel_rebuild_period = G_SEL_REBUILD_PERIOD;
static const t_prune_prog	g_sel_extra_period_deep = G_SEL_EXTRA_PERIOD_DEEP;
static const int			g_sel_depth_threshold_0 = G_SEL_DEPTH_THRESHOLD_0;
static const int			g_sel_depth_threshold_1 = G_SEL_DEPTH_THRESHOLD_1;

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
	period = g_sel_rebuild_period;
	if (node->cur_depth > g_sel_depth_threshold_0)
		period += g_sel_extra_period_deep;
	if (node->cur_depth > g_sel_depth_threshold_1)
		period += g_sel_extra_period_deep;
	if (unset_ratio > 0.0)
		period = (t_prune_prog)(period / unset_ratio);
	else
		period = 99999999;
	config->rebuild_period = period;
	if (node->sub_node_depth > 0)
		config->rebuild_period = 0;
	config->start_cell_idx = -1;
	config->start_cell_val = 1;
	config->is_selective = 0;
}
