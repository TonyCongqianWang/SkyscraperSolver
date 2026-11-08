/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_result.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef SEARCH_RESULT_H
# define SEARCH_RESULT_H
# include "puzzle_structs.h"

typedef struct s_result_transition
{
	t_node_transition	next;
	int					is_neg;
}	t_result_transition;

/* Exhaustion is independent of execution mode and registration count. */
void	consume_child_result(t_solver_state *puzzle,
			const t_result_transition *transition, const t_sol_info *result,
			t_sol_info *aggregate);
void	finish_candidate_search(t_sol_info *result, const t_node_state *node);

#endif
