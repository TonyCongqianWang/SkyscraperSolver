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

#include "print_io.h"
#include "print_grid.h"
#include "puzzle_structs.h"
#include "puzzle_solver.h"
#include "solution_storage.h"
#include "argument_parsing.h"

#include <string.h>
#include <stdio.h>
#include "string_interface.h"

static void	solve_puzzle_and_print_result(t_puzzle *puzzle);
static void	partial_solve_cpy_and_print_debug(t_puzzle *puzzle, int max_depth);

int	main(int argc, char **argv)
{
	static t_puzzle	puzzle;
	int				parsing_retcode;
	int				has_stdin = 0;
	char			*max_solutions = NULL;

	for (int i = 1; i < argc; i++)
	{
		if (strcmp(argv[i], "--stdin") == 0)
			has_stdin = 1;
	}

	if (has_stdin)
	{
		for (int i = 1; i < argc - 1; i++)
		{
			if (strcmp(argv[i], "-s") == 0)
			{
				max_solutions = argv[i + 1];
				break;
			}
		}
		char line[4096];
		while (fgets(line, sizeof(line), stdin))
		{
			size_t len = strlen(line);
			if (len > 0 && line[len - 1] == '\n')
				line[len - 1] = '\0';
			if (strlen(line) == 0)
				continue;
			
			memset(&puzzle, 0, sizeof(puzzle));
			if (!init_puzzle_from_constr_str(&puzzle, line, max_solutions))
			{
				print_error("Wrong puzzle constraints format.");
				printf("--- END OF RECORD ---\n");
				fflush(stdout);
				continue;
			}
			solve_puzzle(&puzzle, -1);
			print_value("Nodes visited", puzzle.nodes_visited);
			printf("--- END OF RECORD ---\n");
			fflush(stdout);
			free_solution_storage(&puzzle);
		}
		return (0);
	}

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
	t_sol_count				solution_idx;
	int						append_nl;

	solve_puzzle(puzzle, -1);
	print_value("Max solutions", puzzle->max_solutions);
	print_value("Solutions found", puzzle->solutions_found);
	if (puzzle->solutions)
	{
		solution_idx = 0;
		while (solution_idx < puzzle->solutions_found
			&& (solution_idx < puzzle->max_solutions
				|| solution_idx == 0))
		{
			append_nl = solution_idx < puzzle->solutions_found - 1;
			append_nl &= solution_idx < puzzle->max_solutions - 1;
			puzzle->cur_node = puzzle->solutions + solution_idx;
			print_solution_grid(puzzle, append_nl);
			solution_idx++;
		}
	}
	print_value("Nodes visited", puzzle->nodes_visited);
	print_value("Main nodes visited", puzzle->main_nodes_visited);
	print_value("Pruning runs", puzzle->prune_runs_count);
}

static void	partial_solve_cpy_and_print_debug(t_puzzle *puzzle, int max_depth)
{
	int			cell_val;

	solve_puzzle(puzzle, max_depth);
	cell_val = 1;
	while (cell_val <= puzzle->size)
	{
		print_bmp_grid(puzzle, cell_val);
		print_message("");
		cell_val++;
	}
	print_bound_grid(puzzle->cur_node, 0);
	print_message("");
	print_bound_grid(puzzle->cur_node, 1);
	print_message("");
	print_solution_grid(puzzle, 0);
	print_value("Unset", puzzle->cur_node->num_unset);
	print_value("Nodes visited", puzzle->nodes_visited);
	print_value("Main nodes visited", puzzle->main_nodes_visited);
	print_value("Pruning runs", puzzle->prune_runs_count);
	print_message("");
}
