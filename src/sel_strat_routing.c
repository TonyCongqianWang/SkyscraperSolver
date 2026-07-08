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

static const double			g_sel_rebuild_period = 1319;
static const double			g_sel_ord2_coeff = 1934;
static const double			g_sel_ord4_coeff = 70567;

void	select_node_select_config(t_puzzle *puzzle,
			t_node_select_config *config)
{
	t_node_state	*node;
	double			unset_ratio;
	double			x;
	double			period;

	node = puzzle->cur_node;
	config->score_family = SCORE_BRANCHING;
	config->criterion = SELECT_MAX;
	config->enable_cache = 1;
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	period = g_sel_rebuild_period;
	x = 1.0 - unset_ratio;
	period += g_sel_ord2_coeff * x * x;
	period += g_sel_ord4_coeff * x * x * x * x;
	config->rebuild_period = (t_prune_prog)period;
	config->start_cell_idx = -1;
	config->start_cell_val = 1;
	config->selectivity = SELECTIVITY_NONE;
}
