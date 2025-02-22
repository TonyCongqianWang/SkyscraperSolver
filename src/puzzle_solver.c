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
#include "cell_bitmaps.h"
#include "transition_scoring.h"
#include "shallow_search.h"

int	solve_puzzle(t_puzzle *puzzle)
{
	return (tree_search(puzzle, -1));
}

int	tree_search(t_puzzle *puzzle, int depth)
{
	t_node_state		old_state;
	t_node_transition	next;

	puzzle->nodes_visited++;
	if (depth == 0
		|| puzzle->node_state.is_complete
		|| puzzle->node_state.is_invalid)
		return (!puzzle->node_state.is_invalid);
	tighten_grid_cell_bounds(puzzle, 0);
	old_state = puzzle->node_state;
	while (try_get_next_transition(puzzle, &next))
	{
		set_grid_val(puzzle, next.cell_idx, next.cell_val, 1);
		if (tree_search(puzzle, depth - 1))
			return (1);
		set_value_invalid(&old_state, next.cell_idx, next.cell_val);
		puzzle->node_state = old_state;
		unset_grid_val(puzzle, next.cell_idx);
	}
	return (0);
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

	if (puzzle->node_state.is_invalid)
		return (0);
	next->score = -1;
	cell_idx = 0;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		cell_idx++;
		if (puzzle->grid_vals[cell_idx - 1] != 0)
			continue ;
		set_best_transition_val(puzzle, cell_idx - 1, &candidate);
		score_transition_full(&puzzle->node_state, &candidate);
		if (candidate.score > next->score)
			*next = candidate;
	}
	return (1);
}
