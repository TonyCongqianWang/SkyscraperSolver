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
#include "grid_interface.h"
#include "strategy_routing.h"
#include "node_selection.h"
#include "solution_storage.h"
#include "solution_info.h"
#include "node_selection_cache.h"

int	has_reached_terminal_state(t_node_state *cur_node)
{
	int				is_leaf_node;

	is_leaf_node = (cur_node->cur_depth >= cur_node->max_depth);
	is_leaf_node |= cur_node->is_complete;
	is_leaf_node |= cur_node->is_invalid;
	return (is_leaf_node);
}

t_sol_info	handle_leaf_node(t_puzzle *puzzle)
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
	if (has_reached_terminal_state(puzzle->cur_node))
		return (handle_leaf_node(puzzle));
	set_cell_val(puzzle, next.cell_idx, next.cell_val,
		(t_check_mode)puzzle->lookahead_check_mode);
	puzzle->cur_node->cur_depth++;
	return (tree_search(puzzle));
}

t_sol_info	tree_search(t_puzzle *puzzle)
{
	t_search_frame		frames[MAX_STACK_DEPTH];
	int					d;
	int					start_d;

	start_d = puzzle->node_stack_top;
	d = start_d;
	puzzle->nodes_visited++;
	if (puzzle->cur_node->sub_node_depth == 0)
		puzzle->main_nodes_visited++;
	if (has_reached_terminal_state(puzzle->cur_node))
		return (handle_leaf_node(puzzle));
	init_sol_info(&frames[d].node_sols, puzzle->squared_size, 0);
	while (1)
	{
		if (process_frame(puzzle, &d, start_d, frames) == SEARCH_TERMINATE)
			break ;
	}
	return (frames[start_d].node_sols);
}
