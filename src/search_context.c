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
#include "lookahead_marks.h"
#include "node_selection_transition.h"

void	enter_lookahead(t_node_state *node, t_lookahead_ctx *ctx,
			t_selectivity_level selectivity, t_search_scope *saved)
{
	saved->policy = node->search_policy;
	saved->cursor = node->lookahead_ctx;
	init_lookahead_marks(ctx, saved->cursor);
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

void	init_root_search_policy(t_node_state *node)
{
	node->search_policy.mode = SEARCH_DFS;
	node->search_policy.leaf_check_mode = g_check_constr;
	node->search_policy.branch.cache_refresh = CACHE_REFRESH_STALE;
	node->search_policy.branch.eligibility = CANDIDATES_VALID;
	node->search_policy.limits.max_solutions = node->solver->max_solutions;
	set_search_bounds(node, node->size * node->size, 0);
}
