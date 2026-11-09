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
#include "cell_distance.h"
#include "line_order.h"
#include "cell_bounds.h"
#include "solution_storage.h"
#include "node_selection_cache.h"
#include "entropy.h"
#include "node_init.h"
#include "params_math.h"
#include "params_depth_arrays.h"
#include "node_selection_score.h"

static void	init_constraint(t_solver_state *puzzle, int idx, int size);
static void	init_puzzle_entropy(t_solver_state *puzzle, int size);

static void	init_puzzle_entropy(t_solver_state *puzzle, int size)
{
	t_node_state	*node;
	int				tier;

	init_depth_arrays(size, puzzle->squared_size);
	node = puzzle->cur_node;
	node->domain.remaining_entropy = compute_initial_entropy(node, size);
	puzzle->max_entropy = node->domain.remaining_entropy;
	tier = 0;
	while (tier < PRUNE_TIER_COUNT)
		node->last_entropy[tier++] = node->domain.remaining_entropy;
}

static void	init_constraints_all(t_solver_state *puzzle, int size)
{
	int		idx;

	idx = 0;
	while (idx < 2 * size)
	{
		init_constraint(puzzle, idx, size);
		idx++;
	}
}

int	init_puzzle(t_solver_state *puzzle, int size, t_sol_count max_sols)
{
	puzzle->size = size;
	puzzle->squared_size = size * size;
	puzzle->selection_lut = make_selection_lut(size, get_sel_power_cell(size),
			get_sel_power_constr(size),
			get_sel_weight_cell_constr_ratio(size));
	init_cell_distance_order(puzzle, size);
	puzzle->constr_max_entropy = size * get_log2_scaled(size)
		* get_weight_constr(size) / ENTROPY_SCALE;
	if (!init_solution_storage(puzzle, max_sols))
		return (0);
	puzzle->nodes_visited = 0;
	puzzle->main_nodes_visited = 0;
	puzzle->prune_runs_count = 0;
	puzzle->constr_bounds.size = size;
	init_order_stacks(puzzle);
	puzzle->node_stack_top = 0;
	puzzle->cur_node = &puzzle->node_stack[0];
	puzzle->cur_node->solver = puzzle;
	init_root_node(puzzle->cur_node, size);
	init_constraints_all(puzzle, size);
	init_puzzle_entropy(puzzle, size);
	init_line_order_stack(puzzle);
	return (1);
}

static void	init_constraint(t_solver_state *puzzle, int idx, int size)
{
	int		sub_index;
	int		grid_index;

	sub_index = 0;
	grid_index = 0;
	puzzle->constraint_pairs[idx].fwd_val = 0;
	puzzle->constraint_pairs[idx].bwd_val = 0;
	while (sub_index < size)
	{
		if (idx < size)
			grid_index = idx + sub_index * size;
		else if (idx < 2 * size)
			grid_index = (idx % size) * size + sub_index;
		puzzle->cur_node->domain.constrs.num_val_positions[idx][sub_index]
			= size;
		puzzle->constraint_pairs[idx].grid_indeces[sub_index] = grid_index;
		puzzle->grid_constr_map[grid_index][idx / size] = idx;
		sub_index++;
	}
}
