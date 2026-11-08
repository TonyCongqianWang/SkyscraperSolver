/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_context.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "search_context.h"
#include "node_selection_transition.h"

void	enter_lookahead(t_node_state *node, t_lookahead_ctx *ctx,
			t_selectivity_level selectivity, t_search_scope *saved)
{
	saved->policy = node->search_policy;
	saved->cursor = node->lookahead_ctx;
	node->search_policy.mode = SEARCH_LOOKAHEAD;
	node->search_policy.branch.cache_refresh = CACHE_REFRESH_REQUIRED;
	node->search_policy.branch.eligibility = CANDIDATES_LOOKAHEAD;
	ctx->selectivity = selectivity;
	node->lookahead_ctx = ctx;
}

void	leave_lookahead(t_node_state *node, const t_search_scope *saved)
{
	node->search_policy = saved->policy;
	node->lookahead_ctx = saved->cursor;
}

void	enter_probe(t_solver_state *puzzle, int depth, t_node_state *saved)
{
	t_node_state	*node;
	int				target;

	node = puzzle->cur_node;
	*saved = *node;
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
	node->search_policy.limits.max_solutions = 1;
	set_search_bounds(node, node->tree.depth + depth, target);
	node->tree.lookahead_depth++;
}

void	leave_probe(t_solver_state *puzzle, const t_node_state *saved)
{
	*puzzle->cur_node = *saved;
	sync_cache_stacks(puzzle);
}

void	set_search_bounds(t_node_state *node, int max_depth, int target)
{
	node->search_policy.limits.max_depth = max_depth;
	node->search_policy.limits.target_nunset = target;
}
