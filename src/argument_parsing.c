/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   argument_parsing.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "argument_parsing.h"
#include "puzzle_structs.h"
#include "string_interface.h"
#include "rule_checking.h"
#include "solution_storage.h"
#include "print_utility.h"

#define USAGE_STR "Wrong argument count. Expected use: \
skyscraper_solver [-s <max_num_solutions>] <constrait_vals> [<grid_vals>]"

static int	has_set_max_solution_flag(int argc, char **argv);
static int	is_correct_argument_count(int argc, char **argv);
static int	parse_grid_argument(t_puzzle *puzzle, char *grid);

int	init_puzzle_from_argv(t_puzzle *puzzle, int argc, char **argv)
{
	char	*constr;
	char	*grid;
	char	*max_solutions;
	int		set_max_solutions;

	set_max_solutions = has_set_max_solution_flag(argc, argv);
	if (!is_correct_argument_count(argc, argv))
		return (-1);
	grid = (0);
	max_solutions = (0);
	if (set_max_solutions)
		max_solutions = argv[2];
	constr = argv[1 + 2 * set_max_solutions];
	if (argc > 1 + 2 * set_max_solutions)
		grid = argv[2 + 2 * set_max_solutions];
	if (!init_puzzle_from_constr_str(puzzle, constr, max_solutions))
	{
		print_error("Wrong puzzle constraints format.");
		return (-2);
	}
	return (parse_grid_argument(puzzle, grid));
}

static int	has_set_max_solution_flag(int argc, char **argv)
{
	return (argc > 1 && argv[1][0] == '-'
		&& argv[1][1] == 's' && argv[1][2] == '\0');
}

static int	is_correct_argument_count(int argc, char **argv)
{
	int		set_max_solutions;

	set_max_solutions = has_set_max_solution_flag(argc, argv);
	if (argc < 2 + 2 * set_max_solutions || argc > 3 + 2 * set_max_solutions)
	{
		print_error(USAGE_STR);
		return (0);
	}
	return (1);
}

static int	parse_grid_argument(t_puzzle *puzzle, char *grid)
{
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
