/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   tree_search_checks.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "tree_search.h"
#include "solution_info.h"
#include "solution_storage.h"
#include "strategy_routing.h"

/* Include registrations made inside pruning, outside child-result sums. */
void	sync_frame_registrations(t_solver_state *puzzle, t_search_frame *frame)
{
	frame->node_sols.solutions_registered
		= puzzle->solutions_found - frame->registered_start;
}

static int	should_stop_frame(t_solver_state *puzzle, t_search_frame *frame)
{
	if (solution_limit_reached(puzzle))
		return (1);
	return (puzzle->cur_node->search_policy.mode == SEARCH_DFS
		&& (!frame->node_sols.exhausted
			|| check_sol_target(&frame->node_sols, puzzle->cur_node)));
}

static t_search_result	stop_frame(t_solver_state *puzzle, int *d,
						int start_d, t_search_frame *frames)
{
	frames[*d].node_sols.exhausted = 0;
	return (check_backtrack(puzzle, d, start_d, frames));
}

static t_search_result	prune_search_frame(t_solver_state *puzzle, int *d,
						int start_d, t_search_frame *frames)
{
	t_sol_info	result;
	int			tier_processed;

	tier_processed = prune_current_step(puzzle);
	sync_frame_registrations(puzzle, &frames[*d]);
	if (should_stop_frame(puzzle, &frames[*d]))
		return (stop_frame(puzzle, d, start_d, frames));
	if (has_reached_terminal_state(puzzle->cur_node))
	{
		result = handle_leaf_node(puzzle);
		update_sol_info(&result, &frames[*d].node_sols);
		return (check_backtrack(puzzle, d, start_d, frames));
	}
	if (tier_processed)
		return (SEARCH_CONTINUE);
	return (SEARCH_PROCEED_TO_BRANCH);
}

t_search_result	check_search_frame(t_solver_state *puzzle, int *d,
					int start_d, t_search_frame *frames)
{
	sync_frame_registrations(puzzle, &frames[*d]);
	if (should_stop_frame(puzzle, &frames[*d]))
		return (stop_frame(puzzle, d, start_d, frames));
	if (puzzle->cur_node->search_policy.mode == SEARCH_LOOKAHEAD)
		return (SEARCH_PROCEED_TO_BRANCH);
	return (prune_search_frame(puzzle, d, start_d, frames));
}
