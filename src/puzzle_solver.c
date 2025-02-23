/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   puzzle_solver.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:27 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "puzzle_solver.h"
#include "grid_update.h"
#include "transition_scoring.h"
#include "shallow_search.h"

int	solve_puzzle(t_puzzle *puzzle)
{
	return (tree_search(puzzle, -1));
}

static int	is_leaf_node(t_node_state *state)
{
	return (state->is_complete
		|| state->is_invalid);
}

int	tree_search(t_puzzle *puzzle, int depth)
{
	t_node_state		old_state;
	t_node_transition	next;

	puzzle->nodes_visited++;
	if (depth == 0 || is_leaf_node(&puzzle->node_state))
		return (!puzzle->node_state.is_invalid);
	tighten_grid_cell_bounds(puzzle, 0);
	while (try_get_next_transition(puzzle, &next))
	{
		old_state = puzzle->node_state;
		set_grid_val(&puzzle->node_state, next.cell_idx, next.cell_val, 0);
		if (tree_search(puzzle, depth - 1))
			return (1);
		puzzle->node_state = old_state;
		set_value_invalid(&puzzle->node_state, next.cell_idx, next.cell_val);
	}
	return (!puzzle->node_state.is_invalid);
}

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
		if (!is_valid_value(&puzzle->node_state, idx, cell_val + 1))
			continue ;
		cur.cell_val = cell_val + 1;
		score_transition_constrs(&puzzle->node_state, &cur);
		if (cur.score > next->score)
			(*next) = cur;
	}
	return (next->cell_val);
}

int	try_get_next_transition(t_puzzle *puzzle, t_node_transition *next)
{
	t_node_transition	candidate;
	int					cell_idx;

	if (is_leaf_node(&puzzle->node_state))
		return (0);
	next->score = -1;
	cell_idx = 0;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		if (is_cell_empty(&puzzle->node_state, cell_idx))
		{
			set_best_transition_val(puzzle, cell_idx, &candidate);
			score_transition_full(&puzzle->node_state, &candidate);
			if (candidate.score > next->score)
				*next = candidate;
		}
		cell_idx++;
	}
	return (1);
}
