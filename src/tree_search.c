/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   tree_search.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:27 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "tree_search.h"
#include "grid_manipulation.h"
#include "node_pruning.h"
#include "node_selection.h"
#include "solution_storage.h"
#include "solution_info.h"

static int	has_reached_terminal_state(t_node_state *cur_node)
{
	int				is_leaf_node;

	is_leaf_node = (cur_node->cur_depth >= cur_node->max_depth);
	is_leaf_node |= cur_node->is_complete;
	is_leaf_node |= cur_node->is_invalid;
	return (is_leaf_node);
}

static t_sol_info	handle_leaf_node(t_puzzle *puzzle)
{
	t_node_state	*cur_node;
	t_sol_info		node_sols;

	cur_node = puzzle->cur_node;
	if (cur_node->is_invalid)
		init_sol_info(&node_sols, puzzle->squared_size, 0);
	else
		init_sol_info(&node_sols, cur_node->num_unset, 1);
	store_node_if_solution(puzzle);
	return (node_sols);
}

t_sol_info	tree_recursion(t_puzzle *puzzle, t_node_transition next)
{
	t_node_state		*cur_node;

	if (has_reached_terminal_state(puzzle->cur_node))
		return (handle_leaf_node(puzzle));
	cur_node = puzzle->cur_node;
	set_grid_val(cur_node, next.cell_idx, next.cell_val, 0);
	cur_node->cur_depth++;
	return (tree_search(puzzle));
}

static void	search_step(t_puzzle *puzzle, t_sol_info *node_sols,
				t_node_transition next)
{
	t_node_state	old_state;
	t_sol_info		recursive_sols;

	old_state = *(puzzle->cur_node);
	update_sol_target(node_sols, puzzle->cur_node);
	recursive_sols = tree_recursion(puzzle, next);
	*(puzzle->cur_node) = old_state;
	if (update_sol_info(&recursive_sols, node_sols)
		|| !check_sol_target(node_sols, puzzle->cur_node)
		|| recursive_sols.min_nunset == puzzle->squared_size)
	{
		set_value_invalid(puzzle->cur_node, next.cell_idx, next.cell_val);
		prune_node(puzzle);
	}
}

t_sol_info	tree_search(t_puzzle *puzzle)
{
	t_node_transition	next;
	t_sol_info			node_sols;
	t_sol_info			recursive_sols;

	puzzle->nodes_visited++;
	if (has_reached_terminal_state(puzzle->cur_node))
		return (handle_leaf_node(puzzle));
	init_node_transition(&next);
	init_sol_info(&node_sols, puzzle->squared_size, 0);
	prune_node(puzzle);
	while (!check_sol_target(&node_sols, puzzle->cur_node)
		&& (try_get_best_transition(puzzle, &next)
			|| has_reached_terminal_state(puzzle->cur_node)))
	{
		if (has_reached_terminal_state(puzzle->cur_node))
		{
			recursive_sols = handle_leaf_node(puzzle);
			update_sol_info(&recursive_sols, &node_sols);
			break ;
		}
		search_step(puzzle, &node_sols, next);
	}
	return (node_sols);
}
