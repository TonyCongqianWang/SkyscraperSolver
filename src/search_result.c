/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_result.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "search_result.h"
#include "solution_info.h"
#include "grid_interface.h"

void	consume_child_result(t_solver_state *puzzle,
			const t_result_transition *transition, const t_sol_info *result,
			t_sol_info *aggregate)
{
	if (aggregate)
		update_sol_info(result, aggregate);
	if (!result->exhausted)
		return ;
	if (transition->is_neg)
		set_cell_val(puzzle, transition->next.cell_idx,
			transition->next.cell_val, g_check_constr);
	else
		set_cell_invalid(puzzle, transition->next.cell_idx,
			transition->next.cell_val, g_check_constr);
}

void	finish_candidate_search(t_sol_info *result, const t_node_state *node)
{
	if (node->domain.is_invalid)
		result->exhausted = 1;
	else if (node->search_policy.branch.eligibility != CANDIDATES_VALID)
		result->exhausted = 0;
}
