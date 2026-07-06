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

static int	insert_initial_grid(t_puzzle *puzzle)
{
	int				idx;
	int				input_val;
	t_node_state	input_state;
	t_grid_update	updates[MAX_CELL_COUNT];
	int				count;

	input_state = *(puzzle->cur_node);
	idx = 0;
	while (idx < puzzle->squared_size)
		puzzle->cur_node->grid.vals[idx++] = 0;
	idx = 0;
	count = 0;
	while (idx < puzzle->squared_size)
	{
		idx++;
		input_val = input_state.grid.vals[idx - 1];
		if (input_val == 0)
			continue ;
		if (puzzle->cur_node->grid.vals[idx - 1] == 0)
		{
			updates[count].cell_idx = idx - 1;
			updates[count].val = input_val;
			count++;
		}
		else if (puzzle->cur_node->grid.vals[idx - 1] != input_val)
			return (0);
	}
	if (count > 0)
	{
		if (!set_cell_vals_batch(puzzle, updates, count, CHECK_CONSTR))
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
