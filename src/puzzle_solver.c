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
#include "shallow_search.h"
#include "node_selection.h"

int	solve_puzzle(t_puzzle *puzzle)
{
	return (tree_search(puzzle, -1));
}

static int	has_reached_terminal_state(t_puzzle *puzzle)
{
	int	is_leaf_node;

	is_leaf_node = puzzle->cur_node->is_complete;
	is_leaf_node |= puzzle->cur_node->is_invalid;
	return (is_leaf_node);
}

static int	node_is_valid(t_puzzle *puzzle)
{
	return (!puzzle->cur_node->is_invalid);
}

int	tree_search(t_puzzle *puzzle, int depth)
{
	t_node_state		old_state;
	t_node_state		*old_storage;
	t_node_transition	next;

	old_state = *(puzzle->cur_node);
	old_storage = puzzle->cur_node;
	puzzle->nodes_visited++;
	if (depth == 0 || has_reached_terminal_state(puzzle))
		return (node_is_valid(puzzle));
	reduce_grid_cell_options(puzzle, 0);
	while (!has_reached_terminal_state(puzzle)
		&& try_get_next_transition(puzzle, &next))
	{
		set_grid_val(puzzle->cur_node, next.cell_idx, next.cell_val, 0);
		if (tree_search(puzzle, depth - 1))
			return (1);
		puzzle->cur_node = &old_state;
		set_value_invalid(puzzle->cur_node, next.cell_idx, next.cell_val);
		puzzle->cur_node = old_storage;
		*(puzzle->cur_node) = old_state;
	}
	return (node_is_valid(puzzle));
}
