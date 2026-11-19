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
#include "math_utils.h"
#include "params_double.h"
#include "params_cache_period.h"
#include <limits.h>

static double	selection_period(t_solver_state *puzzle)
{
	double	raw;
	int		rem;

	rem = puzzle->cur_node->domain.remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem) / rem;
	return ((g_sel_period_coef_sqrt * dsqrt_approx(raw)
			+ g_sel_period_coef_inv * raw)
		* get_sel_period_scale(puzzle->size));
}

static int	bound_period(double period)
{
	if (period <= 0.0)
		return (0);
	if (period >= INT_MAX)
		return (INT_MAX);
	return ((int)period);
}

void	select_node_select_config(t_solver_state *puzzle,
			t_node_select_config *config)
{
	double	period;
	int		i;

	config->criterion = SELECT_MAX;
	period = selection_period(puzzle);
	i = -1;
	while (++i < ORDER_REFRESH_COUNT)
		config->refresh_period[i] = bound_period(period
				* get_cache_period_scale(puzzle->size, i));
	config->selectivity = SELECTIVITY_NONE;
}
