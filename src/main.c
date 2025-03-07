/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "print_utility.h"
#include "print_grid.h"
#include "puzzle_structs.h"
#include "puzzle_solver.h"
#include "solution_storage.h"
#include "argument_parsing.h"

static void	solve_puzzle_and_print_result(t_puzzle *puzzle);
static void	partial_solve_cpy_and_print_debug(t_puzzle puzzle, int max_depth);

int	main(int argc, char **argv)
{
	t_puzzle	puzzle;
	int			parsing_retcode;

	parsing_retcode = init_puzzle_from_argv(&puzzle, argc, argv);
	if (parsing_retcode != 0)
	{
		free_solution_storage(&puzzle);
		return (parsing_retcode);
	}
	(void)&partial_solve_cpy_and_print_debug;
	solve_puzzle_and_print_result(&puzzle);
	free_solution_storage(&puzzle);
	return (0);
}

static void	solve_puzzle_and_print_result(t_puzzle *puzzle)
{
	unsigned long long		solution_idx;
	int						append_nl;

	solve_puzzle(puzzle, -1);
	print_value("Max solutions", puzzle->max_solutions);
	print_value("Solutions found", puzzle->solutions_found);
	if (puzzle->solutions)
	{
		solution_idx = 0;
		while (solution_idx < puzzle->solutions_found
			&& solution_idx < puzzle->max_solutions)
		{
			append_nl = solution_idx < puzzle->solutions_found - 1;
			append_nl &= solution_idx < puzzle->max_solutions - 1;
			puzzle->cur_node = puzzle->solutions + solution_idx;
			print_solution_grid(puzzle, append_nl);
			solution_idx++;
		}
	}
	print_value("Nodes visited", puzzle->nodes_visited);
}

static void	partial_solve_cpy_and_print_debug(t_puzzle puzzle, int max_depth)
{
	int			cell_val;

	puzzle.cur_node = &puzzle.stored_node;
	puzzle.cur_node->puzzle = &puzzle;
	solve_puzzle(&puzzle, max_depth);
	cell_val = 1;
	while (cell_val <= puzzle.size)
	{
		print_bmp_grid(&puzzle, cell_val);
		print_message("");
		cell_val++;
	}
	print_bound_grid(puzzle.cur_node, 0);
	print_message("");
	print_bound_grid(puzzle.cur_node, 1);
	print_message("");
	print_solution_grid(&puzzle, 0);
	print_value("Unset", puzzle.cur_node->num_unset);
	print_value("Nodes visited", puzzle.nodes_visited);
	print_message("");
}
