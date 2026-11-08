/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_leaf.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "tree_search.h"
#include "solution_info.h"
#include "solution_storage.h"

t_leaf_state	classify_search_leaf(const t_node_state *node)
{
	if (node->domain.is_invalid)
		return (LEAF_INVALID);
	if (node->domain.is_complete)
		return (LEAF_COMPLETE);
	if (node->tree.depth >= node->search_policy.limits.max_depth)
		return (LEAF_DEPTH_LIMIT);
	if (node->search_policy.limits.target_nunset > 0
		&& node->domain.num_unset <= node->search_policy.limits.target_nunset)
		return (LEAF_PROGRESS_LIMIT);
	return (LEAF_NONE);
}

t_sol_info	handle_leaf_node(t_solver_state *puzzle)
{
	t_node_state	*cur_node;
	t_sol_info		node_sols;

	cur_node = puzzle->cur_node;
	init_sol_info(&node_sols, cur_node->domain.is_invalid, 0);
	if (!cur_node->domain.is_invalid && cur_node->domain.is_complete)
	{
		node_sols.solutions_registered = store_node_if_solution(puzzle);
		node_sols.exhausted = (node_sols.solutions_registered > 0);
	}
	return (node_sols);
}

int	has_reached_terminal_state(t_node_state *node)
{
	return (classify_search_leaf(node) != LEAF_NONE);
}
