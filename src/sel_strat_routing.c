/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sel_strat_routing.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 14:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 16:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "strategy_routing.h"

#ifndef G_SEL_REBUILD_PERIOD
# define G_SEL_REBUILD_PERIOD 4
#endif

#ifndef G_SEL_EXTRA_PERIOD_DEEP
# define G_SEL_EXTRA_PERIOD_DEEP 128
#endif

#ifndef G_SEL_DEPTH_THRESHOLD_0
# define G_SEL_DEPTH_THRESHOLD_0 2
#endif

#ifndef G_SEL_LINEAR_COEFF
# define G_SEL_LINEAR_COEFF 16.0
#endif

#ifndef G_SEL_QUAD_COEFF
# define G_SEL_QUAD_COEFF 0.5
#endif

static const t_prune_prog	g_sel_rebuild_period = G_SEL_REBUILD_PERIOD;
static const t_prune_prog	g_sel_extra_period_deep = G_SEL_EXTRA_PERIOD_DEEP;
static const int			g_sel_depth_threshold_0 = G_SEL_DEPTH_THRESHOLD_0;
static const double			g_sel_linear_coeff = G_SEL_LINEAR_COEFF;
static const double			g_sel_quad_coeff = G_SEL_QUAD_COEFF;

void	select_node_select_config(t_puzzle *puzzle,
			t_node_select_config *config)
{
	t_node_state	*node;
	double			unset_ratio;
	double			x;
	t_prune_prog	period;

	node = puzzle->cur_node;
	config->score_family = SCORE_BRANCHING;
	config->criterion = SELECT_MAX;
	config->enable_cache = 1;
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	period = g_sel_rebuild_period;
	if (node->cur_depth > g_sel_depth_threshold_0)
		period += g_sel_extra_period_deep;
	x = 1.0 - unset_ratio;
	period += (t_prune_prog)(g_sel_linear_coeff * x
			+ g_sel_quad_coeff * x * period);
	config->rebuild_period = period;
	config->start_cell_idx = -1;
	config->start_cell_val = 1;
	config->is_selective = 0;
}
