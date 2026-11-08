/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   solution_storage.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "solution_storage.h"
#include <stdlib.h>
#include <stdint.h>

int	init_solution_storage(t_solver_state *puzzle, t_sol_count max_sols)
{
	puzzle->solutions_found = 0;
	puzzle->max_solutions = max_sols;
	puzzle->solutions = NULL;
	if (max_sols <= 1)
		puzzle->solutions = &puzzle->sol_node_storage;
	else if (max_sols <= SIZE_MAX / sizeof(t_node_state))
		puzzle->solutions = malloc(sizeof(t_node_state) * (size_t)max_sols);
	return (puzzle->solutions != NULL);
}

void	free_solution_storage(t_solver_state *puzzle)
{
	if (puzzle->solutions && puzzle->max_solutions > 1)
		free(puzzle->solutions);
}

void	store_node_if_solution(t_solver_state *puzzle)
{
	if (puzzle->cur_node->tree.lookahead_depth == 0
		&& !puzzle->cur_node->domain.is_invalid
		&& puzzle->cur_node->domain.is_complete)
	{
		if (puzzle->max_solutions <= 1)
			puzzle->solutions[0] = *(puzzle->cur_node);
		else if (puzzle->solutions_found < puzzle->max_solutions)
			puzzle->solutions[puzzle->solutions_found] = *(puzzle->cur_node);
		puzzle->solutions_found++;
	}
}
