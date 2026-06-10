/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 10:40:00 by towang           ###   ########.fr       */
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
	if (next->cell_idx != -1
		&& !is_cell_empty(puzzle->cur_node, next->cell_idx))
		return (0);
	return (next->cell_idx != -1);
}

int	try_get_best_transition(t_puzzle *puzzle, t_node_transition *next)
{
	t_node_select_config	config;

	select_node_select_config(puzzle, &config);
	if (puzzle->cur_node->is_in_lookahead_select)
	{
		config.start_cell_idx = next->cell_idx;
		if (next->cell_idx >= 0)
			config.start_cell_val = next->cell_val + 1;
		else
			config.start_cell_val = 1;
		config.is_selective = puzzle->cur_node->is_selective_lookahead;
#ifdef LOOKAHEAD_SCORE_FAMILY
		config.score_family = LOOKAHEAD_SCORE_FAMILY;
#endif
#ifdef LOOKAHEAD_CRITERION
		config.criterion = LOOKAHEAD_CRITERION;
#endif
	}
	if (config.enable_cache)
		return (get_best_from_cache(puzzle, next, &config));
	return (scan_best_live(puzzle, next, &config));
}

static int	scan_next_live(t_puzzle *puzzle, t_node_transition *next,
				t_node_select_config *config)
{
	int	cell_idx;

	cell_idx = next->cell_idx >= 0 ? next->cell_idx : 0;
	if (next->cell_idx >= 0)
	{
		next->cell_val++;
		if (set_next_valid_val(puzzle, next)
			&& is_cell_empty(puzzle->cur_node, next->cell_idx))
			return (1);
		cell_idx++;
		next->cell_val = 1;
	}
	while (cell_idx < puzzle->squared_size)
	{
		if (is_cell_empty(puzzle->cur_node, cell_idx)
			&& (!puzzle->cur_node->is_in_lookahead_select || !config->is_selective
				|| (puzzle->cur_node->rows_changed_since_prune
					& (1 << (cell_idx / puzzle->size)))
				|| (puzzle->cur_node->cols_changed_since_prune
					& (1 << (cell_idx % puzzle->size)))))
		{
			next->cell_idx = cell_idx;
			next->cell_val = 1;
			if (set_next_valid_val(puzzle, next)
				&& is_cell_empty(puzzle->cur_node, next->cell_idx))
				return (1);
		}
		cell_idx++;
	}
	return (0);
}

int	try_get_next_transition(t_puzzle *puzzle, t_node_transition *next)
{
	t_node_select_config	config;

	if (puzzle->cur_node->is_complete || puzzle->cur_node->is_invalid)
		return (0);
	select_node_select_config(puzzle, &config);
	if (puzzle->cur_node->is_in_lookahead_select)
		config.is_selective = puzzle->cur_node->is_selective_lookahead;
	if (config.enable_cache)
		return (get_next_from_cache(puzzle, next, &config));
	return (scan_next_live(puzzle, next, &config));
}

void	init_node_transition(t_node_transition *tr)
{
	tr->cell_idx = -1;
	tr->cell_val = 1;
	tr->score = 0.0;
	tr->num_valids_col = 0;
	tr->num_valids_row = 0;
	tr->num_valids_cell = 0;
}
