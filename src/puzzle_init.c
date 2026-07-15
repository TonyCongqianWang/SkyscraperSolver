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

static void	init_root_node(t_node_state *puzzle, int size);
static void	init_node_grid(t_node_state *puzzle, int size);
static void	init_constraint(t_puzzle *puzzle, int idx, int size);
static void	init_node_order_ptrs(t_node_state *node);

void	init_puzzle(t_puzzle *puzzle, int size, t_sol_count max_sols)
{
	int		idx;

	puzzle->size = size;
	puzzle->squared_size = size * size;
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
	puzzle->cur_node->remaining_entropy
		= compute_initial_entropy(puzzle->cur_node, size);
	puzzle->max_entropy = puzzle->cur_node->remaining_entropy;
	puzzle->cur_node->last_entropy[0] = puzzle->cur_node->remaining_entropy;
	puzzle->cur_node->last_entropy[1] = puzzle->cur_node->remaining_entropy;
	puzzle->cur_node->last_entropy[2] = puzzle->cur_node->remaining_entropy;
	puzzle->cur_node->last_entropy[3] = puzzle->cur_node->remaining_entropy;
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
	root_node->target_nunset = 0;
	root_node->last_prune_nunset = size * size + 1;
	root_node->rows_changed_since_prune = 0xffff;
	root_node->cols_changed_since_prune = 0xffff;
	root_node->rows_invalid_since_prune = 0xffff;
	root_node->cols_invalid_since_prune = 0xffff;
	root_node->is_in_lookahead_select = 0;
	init_node_order_ptrs(root_node);
	root_node->remaining_entropy = 0;
	root_node->last_entropy[0] = 0;
	root_node->last_entropy[1] = 0;
	root_node->last_entropy[2] = 0;
	root_node->last_entropy[3] = 0;
	root_node->solutions_found = 0;
	root_node->max_solutions = root_node->puzzle->max_solutions;
	init_node_grid(root_node, size);
}

static void	init_node_grid(t_node_state *node, int size)
{
	int		idx;
	int		v;

	idx = 0;
	while (idx < size * size)
	{
		node->grid.vals[idx] = 0;
		node->grid.valid_val_bmps[idx] = 0xffff;
		update_cell_bounds(node, idx);
		node->grid.num_cell_vals[idx] = size;
		v = 0;
		while (v < MAX_SIZE + 1)
		{
			node->lookahead_scores[idx][v] = 0.0;
			v++;
		}
		idx++;
	}
}

static void	init_node_order_ptrs(t_node_state *node)
{
	node->order_cache = &node->puzzle->order_stack.orders[0];
	node->lowest_empty_idx = 0;
}
