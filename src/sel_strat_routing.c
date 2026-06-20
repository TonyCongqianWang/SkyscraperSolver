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

static const t_prune_prog	g_sel_rebuild_period = 5;
static const double			g_sel_linear_coeff = 20;
static const double			g_sel_quad_coeff = 50;

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
	x = 1.0 - unset_ratio;
	period += (t_prune_prog)(g_sel_linear_coeff * x);
	period += (t_prune_prog)(g_sel_quad_coeff * x * x);
	config->rebuild_period = period;
	config->start_cell_idx = -1;
	config->start_cell_val = 1;
	config->selectivity = SELECTIVITY_NONE;
}
