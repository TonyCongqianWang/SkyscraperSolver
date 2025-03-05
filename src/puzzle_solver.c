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
#include "grid_manipulation.h"
#include "node_pruning.h"
#include "node_selection.h"
#include "solution_storage.h"

int	solve_puzzle(t_puzzle *puzzle, int max_depth)
{
	t_node_state	input_state;
	int				idx;
	int				input_val;

	if (max_depth >= 0)
		puzzle->cur_node->max_depth = max_depth;
	input_state = *(puzzle->cur_node);
	idx = 0;
	while (idx < puzzle->size * puzzle->size)
		puzzle->cur_node->grid.vals[idx++] = 0;
	idx = 0;
	while (idx < puzzle->size * puzzle->size)
	{
		idx++;
		input_val = input_state.grid.vals[idx - 1];
		if (input_val == 0)
			continue ;
		if (puzzle->cur_node->grid.vals[idx - 1] == 0)
			set_grid_val(puzzle->cur_node, idx - 1, input_val, 1);
		else if (puzzle->cur_node->grid.vals[idx - 1] != input_val)
			return (0);
	}
	return (tree_search(puzzle));
}

static int	has_reached_terminal_state(t_node_state *cur_node)
{
	int	is_leaf_node;

	is_leaf_node = (cur_node->cur_depth >= cur_node->max_depth);
	is_leaf_node |= cur_node->is_complete;
	is_leaf_node |= cur_node->is_invalid;
	return (is_leaf_node);
}

static int	found_enough_solutions(t_puzzle *puzzle)
{
	if (puzzle->cur_node->sub_node_depth > 0)
		return (1);
	return (puzzle->max_solutions > 0
		&& puzzle->solutions_found >= puzzle->max_solutions);
}

static int	handle_leaf_node(t_puzzle *puzzle)
{
	store_node_if_solution(puzzle);
	return (!puzzle->cur_node->is_invalid);
}

int	tree_search(t_puzzle *puzzle)
{
	int					found_solution;
	t_node_state		old_state;
	t_node_transition	next;

	puzzle->nodes_visited++;
	if (has_reached_terminal_state(puzzle->cur_node))
		return (handle_leaf_node(puzzle));
	found_solution = 0;
	prune_node(puzzle);
	while (!has_reached_terminal_state(puzzle->cur_node)
		&& try_get_best_transition(puzzle, &next))
	{
		old_state = *(puzzle->cur_node);
		set_grid_val(puzzle->cur_node, next.cell_idx, next.cell_val, 0);
		puzzle->cur_node->cur_depth++;
		if (tree_search(puzzle))
		{
			found_solution = 1;
			if (found_enough_solutions(puzzle))
				return (1);
		}
		*(puzzle->cur_node) = old_state;
		set_value_invalid(puzzle->cur_node, next.cell_idx, next.cell_val);
	}
	return (handle_leaf_node(puzzle) || found_solution);
}
