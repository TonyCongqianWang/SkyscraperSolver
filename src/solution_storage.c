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

void	init_solution_storage(t_puzzle *puzzle, unsigned long long max_sols)
{
	puzzle->solutions_found = 0;
	puzzle->max_solutions = max_sols;
	if (max_sols == 1)
		puzzle->solutions = &puzzle->stored_node;
	else if (max_sols > 1)
		puzzle->solutions = malloc(sizeof(t_node_state) * max_sols);
	else
		puzzle->solutions = (0);
}

void	free_solution_storage(t_puzzle *puzzle)
{
	if (puzzle->solutions && puzzle->max_solutions > 1)
		free(puzzle->solutions);
}

void	store_node_if_solution(t_puzzle *puzzle)
{
	if (!puzzle->cur_node->is_invalid
		&& puzzle->cur_node->is_complete
		&& puzzle->cur_node->sub_node_depth == 0)
	{
		if (puzzle->solutions_found < puzzle->max_solutions)
			puzzle->solutions[puzzle->solutions_found] = *(puzzle->cur_node);
		puzzle->solutions_found++;
	}
}
