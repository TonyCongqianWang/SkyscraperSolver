/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection.h"
#include "transition_scoring.h"
#include "node_pruning.h"
#include "grid_availability.h"
#include "strategy_routing.h"
#include "node_selection_cache.h"
#include "node_selection_eval.h"

static int	scan_best_live(t_puzzle *puzzle, t_node_transition *next,
				t_node_select_config *config)
{
	t_node_transition	candidate;
	int					cell_idx;

	next->cell_idx = -1;
	cell_idx = 0;
	while (cell_idx < puzzle->squared_size)
	{
		if (is_cell_empty(puzzle->cur_node, cell_idx))
		{
			set_best_val_strat(puzzle, cell_idx, &candidate, config);
			if (candidate.cell_idx != -1)
			{
				if (next->cell_idx == -1 || is_better(candidate.score,
						next->score, config->criterion))
					*next = candidate;
			}
		}
		cell_idx++;
	}
	return (next->cell_idx != -1);
}

int	try_get_best_transition(t_puzzle *puzzle, t_node_transition *next)
{
	t_node_select_config	config;

	select_node_select_config(puzzle, &config);
	if (puzzle->cur_node->is_in_lookahead_select)
	{
		config.start_cell_idx = next->cell_idx;
		config.start_cell_val = next->cell_val;
		config.is_selective = puzzle->cur_node->is_selective_lookahead;
	}
	if (config.enable_cache)
		return (get_best_from_cache(puzzle, next, &config));
	return (scan_best_live(puzzle, next, &config));
}
