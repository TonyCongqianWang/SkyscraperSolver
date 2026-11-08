/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   lookahead_dive_internal.c                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "lookahead_dive_internal.h"
#include "grid_manipulation.h"
#include "cell_bounds.h"
#include "tree_search.h"
#include "search_context.h"
#include "node_selection.h"
#include "solution_info.h"
#include "node_selection_cache.h"
#include "node_selection_transition.h"

t_probe_result	search_probe(t_solver_state *puzzle, t_node_transition next,
		int depth, t_check_mode mode)
{
	t_sol_info		local_sols;
	t_node_state	saved;
	t_probe_result	result;
	t_probe_request	request;

	request.next = next;
	request.check_mode = mode;
	request.depth = depth;
	if (enter_probe(puzzle, &request, &saved))
		local_sols = tree_search(puzzle);
	else
		local_sols = handle_leaf_node(puzzle);
	result.outcome = local_sols;
	result.status = DIVE_FAIL;
	result.remaining_entropy = -1;
	if (!local_sols.exhausted)
	{
		result.status = DIVE_PASS;
		result.remaining_entropy = puzzle->cur_node->domain.remaining_entropy;
	}
	leave_probe(puzzle, &saved);
	return (result);
}
