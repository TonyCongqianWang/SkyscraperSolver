/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_solver_summary.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/24 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/24 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "print_io.h"
#include "print_grid.h"
#include "work_instrumentation.h"
#include <stdio.h>

/*
** Shared summary contract for standalone and --stdin execution modes.
** Stdin mode adds only a delimiter after the complete result.
*/
static void	print_solver_summary(t_solver_state *puzzle)
{
	print_value("Max solutions", puzzle->max_solutions);
	print_value("Solutions found", puzzle->solutions_found);
	print_value("Nodes visited", puzzle->nodes_visited);
	print_value("Main nodes visited", puzzle->main_nodes_visited);
	print_value("Pruning runs", puzzle->prune_runs_count);
	work_report(puzzle->solutions_found, puzzle->nodes_visited);
	fflush(stdout);
}

/*
** Shared per-puzzle result: same summary, work counters and solution grids.
*/
void	print_solver_result(t_solver_state *puzzle)
{
	t_sol_count	solution_idx;
	int			append_nl;

	print_solver_summary(puzzle);
	if (!puzzle->solutions)
		return ;
	solution_idx = 0;
	while (solution_idx < puzzle->solutions_found
		&& (solution_idx < puzzle->max_solutions || solution_idx == 0))
	{
		append_nl = solution_idx < puzzle->solutions_found - 1;
		append_nl &= solution_idx < puzzle->max_solutions - 1;
		puzzle->cur_node = puzzle->solutions + solution_idx;
		print_solution_grid(puzzle, append_nl);
		solution_idx++;
	}
}
