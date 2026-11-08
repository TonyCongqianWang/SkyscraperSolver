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
#include "search_context.h"
#include "grid_interface.h"
#include "strategy_routing.h"
#include "node_selection.h"
#include "solution_storage.h"
#include "solution_info.h"
#include "node_selection_cache.h"

t_sol_info	tree_search(t_solver_state *puzzle)
{
	t_search_frame		frames[MAX_STACK_DEPTH];
	int					d;
	int					start_d;

	start_d = puzzle->node_stack_top;
	d = start_d;
	puzzle->nodes_visited++;
	if (puzzle->cur_node->tree.lookahead_depth == 0)
		puzzle->main_nodes_visited++;
	if (has_reached_terminal_state(puzzle->cur_node))
		return (handle_leaf_node(puzzle));
	init_sol_info(&frames[d].node_sols, 1, 0);
	while (1)
	{
		if (process_frame(puzzle, &d, start_d, frames) == SEARCH_TERMINATE)
			break ;
	}
	return (frames[start_d].node_sols);
}
