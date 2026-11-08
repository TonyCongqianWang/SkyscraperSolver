/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   tree_search_advance.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "tree_search.h"
#include "lookahead_dive.h"
#include "search_result.h"
#include "solution_info.h"
#include "node_selection_cache.h"

static void	advance_probe(t_solver_state *puzzle, t_search_frame *frame)
{
	t_probe_result				result;
	t_result_transition			transition;
	const t_lookahead_config	*config;

	config = frame->probe_config;
	transition.next = frame->next;
	transition.is_neg = (frame->probe_pass == LOOKAHEAD_NEG);
	if (transition.is_neg)
		result = probe_exclusion(puzzle, frame->next,
				config->max_depth, g_check_constr);
	else
		result = probe_assumption(puzzle, frame->next,
				config->max_depth, config->check_mode);
	if (result.status == DIVE_PASS)
		node_order_record_probe(puzzle->cur_node->order_cache, frame->next,
			frame->probe_pass, result.remaining_entropy);
	consume_child_result(puzzle, &transition, &result.outcome,
		&frame->node_sols);
}

void	advance_search_frame(t_solver_state *puzzle, int *d,
			t_search_frame *frames)
{
	if (puzzle->cur_node->search_policy.mode == SEARCH_LOOKAHEAD)
	{
		advance_probe(puzzle, &frames[*d]);
		return ;
	}
	descend_to_child(puzzle, d, frames);
	if (has_reached_terminal_state(puzzle->cur_node))
	{
		frames[*d].node_sols = handle_leaf_node(puzzle);
		backtrack_to_parent(puzzle, d, frames);
	}
	else
	{
		init_sol_info(&frames[*d].node_sols, 1, 0);
	}
}
