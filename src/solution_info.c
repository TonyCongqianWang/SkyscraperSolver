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
	info->exhausted = exhausted;
	info->solutions_registered = registered;
	return (0);
}

int	update_sol_info(const t_sol_info *child, t_sol_info *aggregate)
{
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
