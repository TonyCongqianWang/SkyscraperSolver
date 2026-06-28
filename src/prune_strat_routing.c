/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_routing.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 14:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 10:45:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "strategy_routing.h"
#include "prune_strat_initial.h"
#include "prune_strat_root.h"
#include "prune_strat_shallow.h"
#include "prune_strat_medium.h"
#include "prune_strat_deep.h"

#include <stdlib.h>

static double	g_routing_shallow_ratio = 0.05008353583779075;
static double	g_routing_medium_ratio = 0.2736100962866644;

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_routing_env(void)
{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("ROUTING_SHALLOW_RATIO");
	if (val)
		g_routing_shallow_ratio = atof(val);
	val = getenv("ROUTING_MEDIUM_RATIO");
	if (val)
		g_routing_medium_ratio = atof(val);
	initialized = 1;
}
#endif

int	prune_current_step(t_puzzle *puzzle)
{
	int	d;

	if (puzzle->cur_node->cur_depth == 0)
	{
		if (puzzle->prune_runs_count == 0)
			return (prune_strat_initial(puzzle));
		else
			return (prune_strat_root(puzzle));
	}
	else
	{
#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
		init_routing_env();
#endif
#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
		init_routing_env();
#endif
		d = puzzle->cur_node->cur_depth;
		if (d <= puzzle->squared_size * g_routing_shallow_ratio)
			return (prune_strat_shallow(puzzle));
		else if (d <= puzzle->squared_size * g_routing_medium_ratio)
			return (prune_strat_medium(puzzle));
		else
			return (prune_strat_deep(puzzle));
	}
}
