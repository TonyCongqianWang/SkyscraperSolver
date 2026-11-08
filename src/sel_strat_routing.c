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
#include "params_double.h"

void	select_node_select_config(t_solver_state *puzzle,
			t_node_select_config *config)
{
	t_node_state	*node;
	double			raw;
	double			term1;
	double			term2;
	int				rem;

	node = puzzle->cur_node;
	config->criterion = SELECT_MAX;
	rem = node->domain.remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem) / rem;
	term1 = g_sel_period_coef_sqrt * dsqrt_approx(raw);
	term2 = g_sel_period_coef_inv * raw;
	config->rebuild_period = (int)(term1 + term2);
	config->selectivity = SELECTIVITY_NONE;
}
