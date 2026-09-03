/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_routing.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "strategy_routing.h"
#include "prune_strat_initial.h"
#include "prune_strat_root.h"
#include "prune_strat_bucket.h"

int	prune_current_step(t_puzzle *puzzle)
{
	int	d;
	int	b;

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
		b = get_depth_bucket(d, puzzle->squared_size, puzzle->size);
		return (prune_strat_depth_bucket(puzzle, b));
	}
}
