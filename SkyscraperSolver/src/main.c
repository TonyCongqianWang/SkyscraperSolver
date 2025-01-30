/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 21:55:56 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "print_utility.h"
#include "puzzle_structs.h"
#include "puzzle_solver.h"
#include "string_interface.h"

int	main(int argc, char **argv)
{
	t_puzzle	puzzle;
	int			cell_val;

	if (argc != 2)
	{
		print_error("Wrong argument count.");
		return (-1);
	}
	if (!init_puzzle_from_str(&puzzle, argv[1]))
	{
		print_error("Wrong argument format.");
		return (-2);
	}
	if (!tree_search(&puzzle, 1))
	{
		print_error("Could not find solution.");
		return (0);
	}
	cell_val = 1;
	while (cell_val <= puzzle.size)
	{
		print_bmp_grid(&puzzle, cell_val, 1);
		cell_val++;
	}
	print_score_grid(&puzzle);
	print_message("");
	print_solution_grid(&puzzle, 1);
	return (0);
}
