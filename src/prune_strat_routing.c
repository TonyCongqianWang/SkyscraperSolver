/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_routing.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 14:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "strategy_routing.h"
#include "prune_initial.h"
#include "prune_root.h"
#include "prune_shallow.h"
#include "prune_medium.h"
#include "prune_deep.h"

static int	should_skip_depth(t_puzzle *puzzle)
{
	int	d;

	d = puzzle->cur_node->cur_depth;
	if (d <= (puzzle->squared_size * 2) / 64)
		return (should_skip_prune_shallow(puzzle));
	if (d <= (puzzle->squared_size * 5) / 64)
		return (should_skip_prune_medium(puzzle));
	return (should_skip_prune_deep(puzzle));
}

static void	run_node_pruning_depth(t_puzzle *puzzle)
{
	int	d;

	if (should_skip_depth(puzzle))
		return ;
	d = puzzle->cur_node->cur_depth;
	if (d <= (puzzle->squared_size * 2) / 64)
		prune_shallow(puzzle);
	else if (d <= (puzzle->squared_size * 5) / 64)
		prune_medium(puzzle);
	else
		prune_deep(puzzle);
}

void	prune_current_step(t_puzzle *puzzle)
{
	if (puzzle->cur_node->cur_depth == 0)
	{
		if (puzzle->prune_runs_count == 0)
			prune_initial(puzzle);
		else if (!should_skip_prune_root(puzzle))
			prune_root(puzzle);
	}
	else
		run_node_pruning_depth(puzzle);
}
