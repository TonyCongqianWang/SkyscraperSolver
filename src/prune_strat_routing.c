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

static const double	g_routing_shallow_ratio = 0.105231964035567;
static const double	g_routing_medium_ratio = 0.352562620956447;

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
		d = puzzle->cur_node->cur_depth;
		if (d <= puzzle->squared_size * g_routing_shallow_ratio)
			return (prune_strat_shallow(puzzle));
		else if (d <= puzzle->squared_size * g_routing_medium_ratio)
			return (prune_strat_medium(puzzle));
		else
			return (prune_strat_deep(puzzle));
	}
}
