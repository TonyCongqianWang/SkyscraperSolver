/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_probe_context.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "search_context.h"
#include "tree_search.h"
#include "solution_storage.h"

static void	prepare_probe(t_solver_state *puzzle, int depth)
{
	t_node_state	*node;
	int				target;

	node = puzzle->cur_node;
	if (node->tree.lookahead_depth == 0)
		node->tree.unbounded_depth = node->tree.depth;
	if (depth < 0)
	{
		node->tree.neg_lookahead_depth++;
		depth = -depth;
	}
	target = node->domain.num_unset - depth;
	if (target < 0)
		target = 0;
	node->search_policy.mode = SEARCH_DFS;
	node->search_policy.branch.cache_refresh = CACHE_REFRESH_STALE;
	node->search_policy.branch.eligibility = CANDIDATES_VALID;
	set_search_bounds(node, node->tree.depth + depth, target);
	node->tree.lookahead_depth++;
}

int	enter_probe(t_solver_state *puzzle, const t_probe_request *request,
			t_node_state *saved)
{
	rollback_provisional_solution(puzzle);
	*saved = *puzzle->cur_node;
	prepare_probe(puzzle, request->depth);
	puzzle->cur_node->search_policy.leaf_check_mode = request->check_mode;
	if (has_reached_terminal_state(puzzle->cur_node))
		return (0);
	apply_search_transition(puzzle, request->next, request->check_mode,
		request->depth < 0);
	return (1);
}
