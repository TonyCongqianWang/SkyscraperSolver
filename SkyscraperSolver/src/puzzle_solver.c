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
#include "cell_bounds.h"

int	solve_puzzle(t_puzzle *puzzle)
{
	return (tree_search(puzzle, -1));
}

int	tree_search(t_puzzle *puzzle, int depths)
{
	t_node_state		old_state;
	int					cell_idx;
	short				cell_lb;
	short				cell_ub;

	if (puzzle->node_state.is_complete || depths == 0)
		return (!puzzle->node_state.is_invalid);
	puzzle->nodes_visited++;
	cell_idx = get_next_tree_node(puzzle, &cell_lb, &cell_ub);
	old_state = puzzle->node_state;
	while (cell_lb <= cell_ub)
	{
		set_grid_val(puzzle, cell_idx, cell_ub);
		if (tree_search(puzzle, depths - 1))
			return (1);
		set_value_invalid(&old_state, cell_idx, cell_ub);
		puzzle->node_state = old_state;
		unset_grid_val(puzzle, cell_idx);
		cell_idx = get_next_tree_node(puzzle, &cell_lb, &cell_ub);
	}
	return (0);
}

int	score_search_cell_candidate(t_puzzle *puzzle, int idx)
{
	int		num_valid;
	int		x_edge_dist;
	int		y_edge_dist;
	short	cell_lb;
	short	cell_ub;

	if (puzzle->grid_vals[idx] != 0)
		return (-10 * puzzle->size);
	num_valid = get_cell_num_valids(&puzzle->node_state, idx);
	x_edge_dist = idx % puzzle->size;
	if (x_edge_dist > puzzle->size / 2)
		x_edge_dist = puzzle->size - x_edge_dist;
	y_edge_dist = idx / puzzle->size;
	if (y_edge_dist > puzzle->size / 2)
		y_edge_dist = puzzle->size - y_edge_dist;
	get_cell_bounds(&puzzle->node_state, idx, &cell_lb, &cell_ub);
	return (10 * puzzle->size - 8 * num_valid
		- y_edge_dist - x_edge_dist + cell_ub);
}

int	get_next_tree_node(t_puzzle *puzzle, short *cell_lb, short *cell_ub)
{
	int		cell_idx;

	tighten_grid_cell_bounds(puzzle);
	cell_idx = get_next_tree_search_cell(puzzle);
	get_cell_bounds(&puzzle->node_state, cell_idx, cell_lb, cell_ub);
	return (cell_idx);
}

int	get_next_tree_search_cell(t_puzzle *puzzle)
{
	int		score;
	int		grid_idx;
	int		best_idx;
	int		best_score;

	grid_idx = 0;
	best_idx = 0;
	best_score = -1;
	while (grid_idx < puzzle->size * puzzle->size)
	{
		score = score_search_cell_candidate(puzzle, grid_idx);
		if (score > best_score)
		{
			best_idx = grid_idx;
			best_score = score;
		}
		grid_idx++;
	}
	return (best_idx);
}
