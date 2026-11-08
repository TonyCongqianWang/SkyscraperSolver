/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   tree_search_frame.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "tree_search.h"
#include "solution_storage.h"
#include "search_result.h"
#include "search_context.h"
#include "node_selection_transition.h"
#include "grid_interface.h"
#include "strategy_routing.h"
#include "node_selection.h"
#include "solution_info.h"
#include "node_selection_cache.h"

void	backtrack_to_parent(t_solver_state *puzzle, int *d,
			t_search_frame *frames)
{
	t_sol_info			result;
	t_result_transition	transition;

	result = frames[*d].node_sols;
	leave_search_child(puzzle);
	*d = puzzle->node_stack_top;
	transition.next = frames[*d].next;
	transition.is_neg = 0;
	consume_child_result(puzzle, &transition, &result, &frames[*d].node_sols);
}

void	descend_to_child(t_solver_state *puzzle, int *d,
			t_search_frame *frames)
{
	rollback_provisional_solution(puzzle);
	sync_frame_registrations(puzzle, &frames[*d]);
	frames[*d + 1].registered_start = puzzle->solutions_found;
	enter_search_child(puzzle, frames[*d].next,
		frames[*d].node_sols.solutions_registered);
	*d = puzzle->node_stack_top;
}

t_search_result	check_backtrack(t_solver_state *puzzle, int *d, int start_d,
		t_search_frame *frames)
{
	finalize_valid_depth(&frames[*d].node_sols, puzzle->cur_node);
	if (*d == start_d)
		return (SEARCH_TERMINATE);
	backtrack_to_parent(puzzle, d, frames);
	return (SEARCH_CONTINUE);
}

t_search_result	process_search_frame(t_solver_state *puzzle, int *d,
					int start_d, t_search_frame *frames)
{
	t_search_result	early_res;

	early_res = check_search_frame(puzzle, d, start_d, frames);
	if (early_res != SEARCH_PROCEED_TO_BRANCH)
		return (early_res);
	if (puzzle->cur_node->search_policy.mode == SEARCH_DFS)
		init_node_transition(&frames[*d].next);
	if (!try_select_transition(puzzle, &frames[*d].next))
	{
		finish_candidate_search(&frames[*d].node_sols, puzzle->cur_node);
		return (check_backtrack(puzzle, d, start_d, frames));
	}
	execute_search_transition(puzzle, d, frames);
	return (SEARCH_CONTINUE);
}
