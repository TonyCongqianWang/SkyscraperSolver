/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   puzzle_solver.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 19:22:29 by towang           ###   ########.fr       */
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
	grid_idx = get_next_tree_search_cell(puzzle);
	if (grid_idx < 0)
		return (0);
	grid_val = 1;
	old_state = puzzle->node_state;
	while (grid_val <= puzzle->size)
	{
		set_grid_val(puzzle, grid_idx, grid_val);
		if (tree_search(puzzle, depths - 1))
			return (1);
		puzzle->node_state = old_state;
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
	int		idx;
	int		score;
	int		best_idx;
	int		best_score;

	idx = 0;
	best_idx = -1;
	best_score = 0;
	while (idx < puzzle->size * puzzle->size)
	{
		if (puzzle->grid_vals[idx] == 0)
		{
			score = score_search_cell_candidate(puzzle, idx);
			if (score >= puzzle->size)
			{
				return (-1);
			}
			else if (score > best_score)
			{
				best_idx = idx;
				best_score = score;
			}
		}
		idx++;
	}
	return (best_idx);
}
