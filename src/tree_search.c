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
#include "node_selection_transition.h"
#include "solution_info.h"
#include <stddef.h>

static int	enter_search_run(t_solver_state *puzzle)
{
	if (puzzle->cur_node->search_policy.mode == SEARCH_LOOKAHEAD)
		return (0);
	puzzle->nodes_visited++;
	if (puzzle->cur_node->tree.lookahead_depth == 0)
		puzzle->main_nodes_visited++;
	return (has_reached_terminal_state(puzzle->cur_node));
}

t_sol_info	run_tree_search(t_solver_state *puzzle,
			const t_lookahead_config *config, t_lookahead_pass pass)
{
	t_search_frame	frames[MAX_STACK_DEPTH];
	int				d;
	int				start_d;

	if (enter_search_run(puzzle))
		return (handle_leaf_node(puzzle));
	start_d = puzzle->node_stack_top;
	d = start_d;
	init_sol_info(&frames[d].node_sols, 1, 0);
	init_node_transition(&frames[d].next);
	frames[d].probe_config = config;
	frames[d].probe_pass = pass;
	while (process_search_frame(puzzle, &d, start_d, frames)
		!= SEARCH_TERMINATE)
		;
	return (frames[start_d].node_sols);
}

t_sol_info	tree_search(t_solver_state *puzzle)
{
	return (run_tree_search(puzzle, NULL, LOOKAHEAD_NONE));
}
