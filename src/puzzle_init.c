/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   puzzle_init.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 16:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "puzzle_init.h"
#include "cell_bounds.h"
#include "solution_storage.h"
#include "node_selection_cache.h"
#include "entropy.h"
#include "node_init.h"

static void	init_constraint(t_puzzle *puzzle, int idx, int size);
static void	init_puzzle_entropy(t_puzzle *puzzle, int size);

static void	init_puzzle_entropy(t_puzzle *puzzle, int size)
{
	t_node_state	*node;

	node = puzzle->cur_node;
	node->remaining_entropy = compute_initial_entropy(node, size);
	puzzle->max_entropy = node->remaining_entropy;
	node->last_entropy[0] = node->remaining_entropy;
	node->last_entropy[1] = node->remaining_entropy;
	node->last_entropy[2] = node->remaining_entropy;
	node->last_entropy[3] = node->remaining_entropy;
}

void	init_puzzle(t_puzzle *puzzle, int size, t_sol_count max_sols)
{
	int		idx;

	puzzle->size = size;
	puzzle->squared_size = size * size;
	puzzle->constr_max_entropy = size * g_log2_table[size]
		* g_weight_constr / ENTROPY_SCALE;
	init_solution_storage(puzzle, max_sols);
	puzzle->nodes_visited = 0;
	puzzle->main_nodes_visited = 0;
	puzzle->prune_runs_count = 0;
	puzzle->constr_bounds.size = size;
	init_order_stacks(puzzle);
	puzzle->node_stack_top = 0;
	puzzle->cur_node = &puzzle->node_stack[0];
	puzzle->cur_node->puzzle = puzzle;
	init_root_node(puzzle->cur_node, size);
	idx = 0;
	while (idx < 2 * size)
	{
		init_constraint(puzzle, idx, size);
		idx++;
	}
	init_puzzle_entropy(puzzle, size);
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
