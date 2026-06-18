/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   tree_search.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "tree_search.h"
#include "grid_manipulation.h"
#include "strategy_routing.h"
#include "node_selection.h"
#include "solution_storage.h"
#include "solution_info.h"
#include "node_selection_cache.h"

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
	sync_cache_stacks(puzzle);
	if (update_sol_info(&recursive_sols, node_sols)
		|| !check_sol_target(node_sols, puzzle->cur_node)
		|| recursive_sols.min_nunset == puzzle->squared_size)
	{
		set_value_invalid(puzzle->cur_node, next.cell_idx, next.cell_val);
	}
}

static void	prune_current_step(t_puzzle *puzzle, int is_first_iter)
{
	if (puzzle->cur_node->cur_depth == 0)
	{
		if (puzzle->nodes_visited == 1 && is_first_iter)
			run_prune_initial_fixpoint(puzzle);
		else
			run_prune_root_fixpoint(puzzle);
	}
	else if (is_first_iter)
	{
		run_node_pruning_depth(puzzle);
	}
}

static t_sol_info	handle_terminal_in_loop(t_puzzle *puzzle,
		t_sol_info *node_sols)
{
	t_sol_info	recursive_sols;

	recursive_sols = handle_leaf_node(puzzle);
	update_sol_info(&recursive_sols, node_sols);
	return (*node_sols);
}

t_sol_info	tree_search(t_puzzle *puzzle)
{
	t_node_transition	next;
	t_sol_info			node_sols;
	int					is_first;

	puzzle->nodes_visited++;
	if (has_reached_terminal_state(puzzle->cur_node))
		return (handle_leaf_node(puzzle));
	init_sol_info(&node_sols, puzzle->squared_size, 0);
	is_first = 1;
	while (!check_sol_target(&node_sols, puzzle->cur_node))
	{
		prune_current_step(puzzle, is_first);
		is_first = 0;
		if (has_reached_terminal_state(puzzle->cur_node))
			return (handle_terminal_in_loop(puzzle, &node_sols));
		init_node_transition(&next);
		if (!try_get_best_transition(puzzle, &next))
			break ;
		search_step(puzzle, &node_sols, next);
	}
	return (node_sols);
}
