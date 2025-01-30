/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 21:10:20 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "print_utility.h"
#include "print_grid.h"
#include "puzzle_structs.h"
#include "puzzle_solver.h"
#include "string_interface.h"

void	partial_solve_and_print_bmps(t_puzzle *puzzle, int depths);

int	main(int argc, char **argv)
{
	t_puzzle	puzzle;

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
	partial_solve_and_print_bmps(&puzzle, 1);
	if (!solve_puzzle(&puzzle))
	{
		print_error("Could not find solution.");
		return (0);
	}
	print_solution_grid(&puzzle);
	print_value("Nodes visited", puzzle.nodes_visited);
	return (0);
}

void	partial_solve_and_print_bmps(t_puzzle *puzzle, int depths)
{
	int			cell_val;

	tree_search(puzzle, depths);
	cell_val = 1;
	while (cell_val <= puzzle->size)
	{
		print_bmp_grid(puzzle, cell_val);
		print_message("");
		cell_val++;
	}
	print_bound_grid(&puzzle->node_state, 0);
	print_message("");
	print_bound_grid(&puzzle->node_state, 1);
	print_message("");
	print_score_grid(puzzle);
	print_message("");
	print_solution_grid(puzzle);
}
