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
#include "shallow_search.h"
#include "grid_update.h"

int	set_best_transition_val(t_puzzle *puzzle, int idx, t_node_transition *next)
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

int	try_get_next_transition(t_puzzle *puzzle, t_node_transition *next)
{
	t_node_transition	candidate;
	int					cell_idx;

	next->score = -1;
	cell_idx = 0;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		if (is_cell_empty(puzzle->cur_node, cell_idx))
		{
			set_best_transition_val(puzzle, cell_idx, &candidate);
			score_transition_full(puzzle->cur_node, &candidate);
			if (candidate.score > next->score)
				*next = candidate;
		}
		cell_idx++;
	}
	return (next->score > -1);
}
