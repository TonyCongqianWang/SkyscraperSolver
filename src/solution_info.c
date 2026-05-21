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

int	init_sol_info(t_sol_info *info, int min_nunset, int solutions_found)
{
    info->min_nunset = min_nunset;
    info->solutions_found = solutions_found;
    return (0);
}

int update_sol_info(t_sol_info *n_info, t_sol_info *o_info)
{
    o_info->solutions_found += n_info->solutions_found;
    if (n_info->min_nunset < o_info->min_nunset)
    {
        o_info->min_nunset = n_info->min_nunset;
        return (n_info->solutions_found > 0);
    }
    else
        return (n_info->solutions_found > 0);
}

int check_sol_target(t_sol_info *info, t_node_state *node)
{
    if (node->max_solutions <= 0
        || info->solutions_found < node->max_solutions
        || info->min_nunset > node->target_nunset)
        return (0);
    else
        return (1);
}

int update_sol_target(t_sol_info *info, t_node_state *node)
{
    if (node->max_solutions == 0)
        return (0);
    node->max_solutions -= info->solutions_found;
    if (node->max_solutions <= 0)
    {
        node->max_solutions = 0;
        return (1);
    }
    return (1);
}
