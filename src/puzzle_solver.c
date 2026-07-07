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
#include "tree_search.h"
#include "grid_interface.h"

static void	clear_grid(t_puzzle *puzzle)
{
	int	idx;

	idx = 0;
	while (idx < puzzle->squared_size)
		puzzle->cur_node->grid.vals[idx++] = 0;
}

static int	collect_initial_updates(t_puzzle *puzzle, const t_node_state *input,
				t_grid_update *updates, int *count)
{
	int	idx;
	int	val;

	idx = 0;
	*count = 0;
	while (idx < puzzle->squared_size)
	{
		val = input->grid.vals[idx];
		if (val != 0)
		{
			if (puzzle->cur_node->grid.vals[idx] == 0)
			{
				updates[*count].cell_idx = idx;
				updates[*count].val = val;
				(*count)++;
			}
			else if (puzzle->cur_node->grid.vals[idx] != val)
				return (0);
		}
		idx++;
	}
	return (1);
}

static int	insert_initial_grid(t_puzzle *puzzle)
{
	t_node_state	input_state;
	t_grid_update	updates[MAX_CELL_COUNT];
	int				count;

	input_state = *(puzzle->cur_node);
	clear_grid(puzzle);
	if (!collect_initial_updates(puzzle, &input_state, updates, &count))
		return (0);
	if (count > 0)
	{
		if (!set_cell_vals_batch(puzzle, updates, count, g_check_constr))
			return (0);
	}
	return (1);
}

int	solve_puzzle(t_puzzle *puzzle, int max_depth)
{
	t_sol_info			node_sols;

	if (!insert_initial_grid(puzzle))
		return (0);
	if (max_depth >= 0)
	{
		puzzle->cur_node->target_nunset = puzzle->squared_size - max_depth;
		puzzle->cur_node->max_depth = max_depth;
	}
	node_sols = tree_search(puzzle);
	puzzle->solutions_found = node_sols.solutions_found;
	return (puzzle->solutions_found);
}
