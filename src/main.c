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
#include "rule_checking.h"

#define USAGE_STR "Wrong argument count. Expected use: \
skyscraper_solver [-a] <constrait_vals> [<grid_vals>]"

static void	solve_puzzle_and_print_result(t_puzzle *puzzle);
static void	partial_solve_cpy_and_print_debug(t_puzzle puzzle, int max_depth);
static int	parse_command_line_args(t_puzzle *puzzle, int argc, char **argv);
static int	init_puzzle_from_args(t_puzzle *puzzle, char *constr, char *grid);

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
	solve_puzzle(puzzle, -1);
	if (puzzle->find_all)
	{
		print_value("Solutions found", puzzle->solutions_found);
	}
	else if (puzzle->cur_node->is_invalid)
		print_message("Could not find solution.");
	else
		print_solution_grid(puzzle);
	print_value("Nodes visited", puzzle->nodes_visited);
}

static int	init_puzzle_from_args(t_puzzle *puzzle, char *constr, char *grid)
{
	if (!init_puzzle_from_constr_str(puzzle, constr))
	{
		print_error("Wrong puzzle constraints format.");
		return (-2);
	}
	if (grid)
	{
		if (!set_puzzle_grid_to_str_vals(puzzle, grid))
		{
			print_error("Wrong puzzle grid format.");
			return (-2);
		}
		if (check_rule_violations(puzzle))
		{
			print_error("Grid violates puzzle rules.");
			return (-2);
		}
	}
	return (0);
}

static int	parse_command_line_args(t_puzzle *puzzle, int argc, char **argv)
{
	int		find_all;
	int		ret_code;
	char	*constr;
	char	*grid;

	find_all = 0;
	if (argc > 1 && argv[1][0] == '-'
		&& argv[1][1] == 'a' && argv[1][2] == '\0')
		find_all = 1;
	if (argc < 2 + find_all || argc > 3 + find_all)
	{
		print_error(USAGE_STR);
		return (-1);
	}
	constr = argv[1 + find_all];
	grid = (0);
	if (argc > 1 + find_all)
		grid = argv[2 + find_all];
	ret_code = init_puzzle_from_args(puzzle, constr, grid);
	if (ret_code != 0)
		return (ret_code);
	puzzle->find_all = find_all;
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
