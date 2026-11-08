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
#include "node_selection.h"
#include "solution_info.h"
#include "node_selection_cache.h"
#include "node_selection_transition.h"

static int	transition_node(t_puzzle *puzzle, int depth)
{
	int					target_nunset;
	t_node_state		*cur_node;

	cur_node = puzzle->cur_node;
	target_nunset = cur_node->num_unset - depth;
	if (target_nunset <= 0)
		target_nunset = 0;
	cur_node->search_policy.limits.max_solutions = 1;
	cur_node->search_policy.limits.target_nunset = target_nunset;
	cur_node->search_policy.limits.max_depth = cur_node->tree.depth;
	cur_node->search_policy.limits.max_depth += depth;
	cur_node->tree.lookahead_depth++;
	return (0);
}

static int	begin_dive(t_puzzle *puzzle, int depth)
{
	int	is_neg;

	is_neg = (depth < 0);
	if (is_neg)
	{
		puzzle->cur_node->tree.neg_lookahead_depth++;
		depth = -depth;
	}
	transition_node(puzzle, depth);
	return (is_neg);
}

t_probe_result	search_probe(t_puzzle *puzzle, t_node_transition next,
		int depth, t_check_mode mode)
{
	t_sol_info		local_sols;
	t_node_state	saved;
	t_probe_result	result;

	saved = *puzzle->cur_node;
	begin_dive(puzzle, depth);
	local_sols = tree_recursion(puzzle, next, mode, depth < 0);
	result.status = DIVE_FAIL;
	result.remaining_entropy = -1;
	if (local_sols.solutions_found > 0)
	{
		result.status = DIVE_PASS;
		result.remaining_entropy = puzzle->cur_node->remaining_entropy;
	}
	*puzzle->cur_node = saved;
	sync_cache_stacks(puzzle);
	return (result);
}
