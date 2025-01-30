/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   puzzle_solver.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 19:07:50 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "puzzle_solver.h"
#include "grid_update.h"
#include "cell_bitmaps.h"

int	solve_puzzle(t_puzzle *puzzle)
{
	return (tree_search(puzzle, -1));
}

int	tree_search(t_puzzle *puzzle, int depths)
{
	t_node_state		old_state;
	int					grid_idx;
	int					grid_val;

	if (puzzle->node_state.is_complete || depths == 0)
		return (!puzzle->node_state.is_invalid);
	puzzle->nodes_visited++;
	grid_idx = get_next_tree_search_cell(puzzle);
	grid_val = 1;
	old_state = puzzle->node_state;
	while (grid_val <= puzzle->size)
	{
		if (is_valid_value(&puzzle->node_state, grid_idx, grid_val))
		{
			set_grid_val(puzzle, grid_idx, grid_val);
			if (tree_search(puzzle, depths - 1))
				return (1);
			puzzle->node_state = old_state;
		}
		grid_val++;
	}
	unset_grid_val(puzzle, grid_idx);
	return (0);
}

int	score_search_cell_candidate(t_puzzle *puzzle, int idx)
{
	int				grid_val;
	int				num_valid;

	grid_val = 1;
	num_valid = 0;
	while (grid_val <= puzzle->size)
	{
		if (try_grid_val(puzzle, idx, grid_val))
			num_valid++;
		else
			set_value_invalid(&puzzle->node_state, idx, grid_val);
		grid_val++;
	}
	return (puzzle->size - num_valid);
}

int	get_next_tree_search_cell(t_puzzle *puzzle)
{
	int		loop_idx;
	int		score;
	int		grid_idx;
	int		best_idx;
	int		best_score;

	loop_idx = 0;
	best_idx = 0;
	best_score = -1;
	while (loop_idx < 2 * puzzle->size * puzzle->size)
	{
		grid_idx = loop_idx % (puzzle->size * puzzle->size);
		if (puzzle->grid_vals[grid_idx] == 0)
		{
			score = score_search_cell_candidate(puzzle, grid_idx);
			if (score > best_score)
			{
				best_idx = grid_idx;
				best_score = score;
			}
			if (score >= puzzle->size)
				return (best_idx);
		}
		loop_idx++;
	}
	return (best_idx);
}
