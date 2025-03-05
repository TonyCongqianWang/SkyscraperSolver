/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   puzzle_init.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 21:21:54 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "puzzle_init.h"
#include "cell_bounds.h"
#include "solution_storage.h"

static void	init_root_node(t_node_state *puzzle, int size);
static void	init_node_grid(t_node_state *puzzle, int size);
static void	init_constraint(t_puzzle *puzzle, int idx, int size);

void	init_puzzle(t_puzzle *puzzle, int size, unsigned long long max_sols)
{
	int		idx;

	puzzle->size = size;
	init_solution_storage(puzzle, max_sols);
	puzzle->nodes_visited = 0;
	puzzle->constr_bounds.size = size;
	puzzle->cur_node = &puzzle->stored_node;
	puzzle->cur_node->puzzle = puzzle;
	init_root_node(puzzle->cur_node, size);
	idx = 0;
	while (idx < 2 * size)
	{
		init_constraint(puzzle, idx, size);
		idx++;
	}
}

static void	init_constraint(t_puzzle *puzzle, int idx, int size)
{
	int		sub_index;
	int		grid_index;

	sub_index = 0;
	grid_index = 0;
	while (sub_index < size)
	{
		if (idx < size)
			grid_index = idx + sub_index * size;
		else if (idx < 2 * size)
			grid_index = (idx % size) * size + sub_index;
		puzzle->cur_node->constrs.num_val_positions[idx][sub_index] = size;
		puzzle->constraint_pairs[idx].grid_indeces[sub_index] = grid_index;
		puzzle->grid_constr_map[grid_index][idx / size] = idx;
		sub_index++;
	}
}

static void	init_root_node(t_node_state *root_node, int size)
{
	root_node->size = size;
	root_node->is_complete = 0;
	root_node->is_invalid = 0;
	root_node->sub_node_depth = 0;
	root_node->cur_depth = 0;
	root_node->last_set_idx = -1;
	root_node->max_depth = size * size;
	root_node->num_unset = size * size;
	init_node_grid(root_node, size);
}

static void	init_node_grid(t_node_state *node, int size)
{
	int		idx;

	idx = 0;
	while (idx < size * size)
	{
		node->grid.vals[idx] = 0;
		node->grid.valid_val_bmps[idx] = 0xffff;
		update_cell_bounds(node, idx);
		node->grid.num_cell_vals[idx] = size;
		idx++;
	}
}
