/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_io.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:36 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>
#include "print_io.h"
#include "work_instrumentation.h"

void	put_char(const char ch)
{
	if (!write(1, &ch, 1))
		return ;
}

void	print_message(const char *str)
{
	while (*str)
	{
		put_char(*str);
		str++;
	}
	put_char('\n');
}

void	print_value(const char *descr, unsigned long long value)
{
	while (*descr)
	{
		put_char(*descr);
		descr++;
	}
	put_char(':');
	put_char(' ');
	put_number(value);
	put_char('\n');
}

void	print_error(const char *str)
{
	(void)(write(2, "Error: ", 7) + 1);
	while (*str)
	{
		(void)(write(2, str, 1) + 1);
		str++;
	}
	(void)(write(2, "\n", 1) + 1);
}

void	put_number(unsigned long long nbr)
{
	char	val;

	val = '0';
	if (nbr >= 10)
		put_number(nbr / 10);
	val += nbr % 10;
	put_char(val);
}

/*
** Shared output contract for standalone and --stdin solver invocations.
** Only solution-grid rendering and the stdin instance delimiter differ.
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
