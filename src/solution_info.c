/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   solution_info.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "solution_info.h"

int	init_sol_info(t_sol_info *info, int exhausted, t_sol_count registered)
{
	info->min_valid_depth = VALID_DEPTH_UNSET;
	info->exhausted = exhausted;
	info->solutions_registered = registered;
	return (0);
}

int	update_sol_info(const t_sol_info *child, t_sol_info *aggregate)
{
	if (child->min_valid_depth != VALID_DEPTH_UNSET
		&& (aggregate->min_valid_depth == VALID_DEPTH_UNSET
			|| child->min_valid_depth < aggregate->min_valid_depth))
		aggregate->min_valid_depth = child->min_valid_depth;
	aggregate->solutions_registered += child->solutions_registered;
	aggregate->exhausted &= child->exhausted;
	return (child->exhausted);
}

int	check_sol_target(t_sol_info *info, t_node_state *node)
{
	return (node->search_policy.limits.max_solutions > 0
		&& info->solutions_registered
		>= node->search_policy.limits.max_solutions);
}

int	get_valid_depth(const t_node_state *node)
{
	if (node->domain.is_invalid)
		return (node->tree.depth - 1);
	return (node->tree.depth);
}

void	finalize_valid_depth(t_sol_info *result, const t_node_state *node)
{
	if (result->min_valid_depth == VALID_DEPTH_UNSET
		|| (node->domain.is_invalid
			&& get_valid_depth(node) < result->min_valid_depth))
		result->min_valid_depth = get_valid_depth(node);
}
