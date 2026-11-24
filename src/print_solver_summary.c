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
#include "work_instrumentation.h"

/*
** Shared summary contract for standalone and --stdin execution modes.
** Only solution grids and the stdin instance delimiter differ.
*/
void	print_solver_summary(t_solver_state *puzzle)
{
	print_value("Max solutions", puzzle->max_solutions);
	print_value("Solutions found", puzzle->solutions_found);
	print_value("Nodes visited", puzzle->nodes_visited);
	print_value("Main nodes visited", puzzle->main_nodes_visited);
	print_value("Pruning runs", puzzle->prune_runs_count);
	work_report(puzzle->solutions_found, puzzle->nodes_visited);
}
