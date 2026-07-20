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
#include "entropy.h"
#include "math_utils.h"
#include <math.h>

static const long long		g_sel_period_scale = 1000000;
static const double			g_sel_period_coef_sqrt = 5;
static const double			g_sel_period_coef_inv = 13;

void	select_node_select_config(t_puzzle *puzzle,
			t_node_select_config *config)
{
	t_node_state	*node;
	double			raw;
	double			term1;
	double			term2;
	int				rem;

	node = puzzle->cur_node;
	config->score_family = SCORE_BRANCHING;
	config->criterion = SELECT_MAX;
	config->enable_cache = 1;
	rem = node->remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem)
		* g_sel_period_scale / rem;
	term1 = g_sel_period_coef_sqrt * sqrt(raw);
	term2 = g_sel_period_coef_inv * (raw / 1000.0);
	config->rebuild_period = (int)(term1 + term2);
	config->start_cell_idx = -1;
	config->start_cell_val = 1;
	config->selectivity = SELECTIVITY_NONE;
}
