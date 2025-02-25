/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:27 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection.h"
#include "transition_scoring.h"
#include "node_pruning.h"
#include "grid_update.h"
#include "cell_bounds.h"

static int	set_next_valid_val(t_puzzle *puzzle, t_node_transition *next);
static int	set_best_val(t_puzzle *puzzle, int idx, t_node_transition *next);

int	try_get_next_transition(t_puzzle *puzzle, t_node_transition *next)
{
	int		cell_idx;

	if (puzzle->cur_node->is_complete || puzzle->cur_node->is_invalid)
		return (0);
	cell_idx = next->cell_idx;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		if (is_cell_empty(puzzle->cur_node, cell_idx))
		{
			next->cell_idx = cell_idx;
			if (set_next_valid_val(puzzle, next))
				return (1);
		}
		cell_idx++;
		next->cell_val = 1;
	}
	return (0);
}

int	try_get_best_transition(t_puzzle *puzzle, t_node_transition *next)
{
	t_node_transition	candidate;
	int					cell_idx;

	next->score = -1;
	cell_idx = 0;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		if (is_cell_empty(puzzle->cur_node, cell_idx))
		{
			set_best_val(puzzle, cell_idx, &candidate);
			score_transition_full(puzzle->cur_node, &candidate);
			if (candidate.score > next->score)
				*next = candidate;
		}
		cell_idx++;
	}
	return (next->score > -1);
}

static int	set_next_valid_val(t_puzzle *puzzle, t_node_transition *next)
{
	short			cell_val;
	short			cell_ub;

	get_cell_bounds(puzzle->cur_node, next->cell_idx, &cell_val, &cell_ub);
	if (cell_val < next->cell_val)
		cell_val = next->cell_val;
	while (cell_val <= cell_ub)
	{
		if (is_valid_value(puzzle->cur_node, next->cell_idx, cell_val))
		{
			next->cell_val = cell_val;
			return (1);
		}
		cell_val++;
	}
	return (0);
}

static int	set_best_val(t_puzzle *puzzle, int idx, t_node_transition *next)
{
	t_node_transition	cur;
	int					cell_val;

	next->score = -1;
	cur.cell_idx = idx;
	cell_val = puzzle->size;
	while (cell_val > 0)
	{
		cell_val--;
		if (!is_valid_value(puzzle->cur_node, idx, cell_val + 1))
			continue ;
		cur.cell_val = cell_val + 1;
		score_transition_constrs(puzzle->cur_node, &cur);
		if (cur.score > next->score)
			(*next) = cur;
	}
	return (next->cell_val);
}
