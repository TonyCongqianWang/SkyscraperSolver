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
	enter_search_child(puzzle, frames[*d].next,
		frames[*d].node_sols.solutions_registered);
	*d = puzzle->node_stack_top;
}

t_search_result	check_backtrack(t_solver_state *puzzle, int *d, int start_d,
		t_search_frame *frames)
{
	if (*d == start_d)
		return (SEARCH_TERMINATE);
	backtrack_to_parent(puzzle, d, frames);
	return (SEARCH_CONTINUE);
}

static t_search_result	check_early_states(t_solver_state *puzzle, int *d,
							int start_d, t_search_frame *frames)
{
	t_sol_info	rec_sols;
	int			pruned;

	if (puzzle->cur_node->search_policy.mode == SEARCH_LOOKAHEAD)
		return (SEARCH_PROCEED_TO_BRANCH);
	if (!frames[*d].node_sols.exhausted
		|| check_sol_target(&frames[*d].node_sols, puzzle->cur_node))
	{
		frames[*d].node_sols.exhausted = 0;
		return (check_backtrack(puzzle, d, start_d, frames));
	}
	pruned = prune_current_step(puzzle);
	if (has_reached_terminal_state(puzzle->cur_node))
	{
		rec_sols = handle_leaf_node(puzzle);
		update_sol_info(&rec_sols, &frames[*d].node_sols);
		return (check_backtrack(puzzle, d, start_d, frames));
	}
	if (pruned)
		return (SEARCH_CONTINUE);
	return (SEARCH_PROCEED_TO_BRANCH);
}

t_search_result	process_search_frame(t_solver_state *puzzle, int *d,
					int start_d, t_search_frame *frames)
{
	t_search_result	early_res;

	early_res = check_early_states(puzzle, d, start_d, frames);
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
