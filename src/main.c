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
#include "string_interface.h"

static void	solve_puzzle_and_print_result(t_puzzle *puzzle);
static void	partial_solve_cpy_and_print_debug(t_puzzle puzzle, int max_depth);
static int	parse_command_line_args(t_puzzle *puzzle, int argc, char **argv);

int	main(int argc, char **argv)
{
	t_puzzle	puzzle;
	int			parsing_retcode;

	parsing_retcode = parse_command_line_args(&puzzle, argc, argv);
	if (parsing_retcode != 0)
		return (parsing_retcode);
	(void)&partial_solve_cpy_and_print_debug;
	solve_puzzle_and_print_result(&puzzle);
	return (0);
}

static void	solve_puzzle_and_print_result(t_puzzle *puzzle)
{
	if (!solve_puzzle(puzzle, -1))
	{
		print_error("Could not find solution.");
		print_value("Nodes visited", puzzle->nodes_visited);
		return ;
	}
	print_solution_grid(puzzle);
	print_value("Nodes visited", puzzle->nodes_visited);
}

static int	parse_command_line_args(t_puzzle *puzzle, int argc, char **argv)
{
	if (argc != 2 && argc != 3)
	{
		print_error("Wrong argument count.");
		return (-1);
	}
	if (!init_puzzle_from_constr_str(puzzle, argv[1]))
	{
		print_error("Wrong argument format.");
		return (-2);
	}
	if (argc == 3)
		set_puzzle_grid_to_str_vals(puzzle, argv[2]);
	return (0);
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
	print_solution_grid(&puzzle);
	print_value("Unset", puzzle.cur_node->num_unset);
	print_value("Nodes visited", puzzle.nodes_visited);
	print_message("");
}
