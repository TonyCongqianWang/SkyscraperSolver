/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   solution_registration.c                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "solution_storage.h"

int	solution_limit_reached(const t_solver_state *puzzle)
{
	return (puzzle->max_solutions > 0
		&& puzzle->solutions_found >= puzzle->max_solutions);
}

/* Only the first hypothesis can complete without speculative branching. */
t_registration_kind	get_solution_registration(const t_solver_state *puzzle)
{
	const t_node_state	*node;

	node = puzzle->cur_node;
	if (node->domain.is_invalid || !node->domain.is_complete
		|| solution_limit_reached(puzzle))
		return (REGISTRATION_NONE);
	if (node->tree.lookahead_depth == 0
		|| node->tree.depth == node->tree.unbounded_depth + 1)
		return (REGISTRATION_PERMANENT);
	if (puzzle->max_solutions > 0
		&& puzzle->max_solutions - puzzle->solutions_found == 1)
		return (REGISTRATION_PROVISIONAL);
	return (REGISTRATION_NONE);
}

/* The pending final slot survives node restoration until search resumes. */
void	rollback_provisional_solution(t_solver_state *puzzle)
{
	if (!puzzle->provisional_solution)
		return ;
	puzzle->solutions_found--;
	puzzle->provisional_solution = 0;
}
