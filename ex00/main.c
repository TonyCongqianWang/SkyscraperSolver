/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/25 18:33:59 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "r01_io.h"
#include "r01_solver.h"
#include "r01_puzzle.h"

int	main(int argc, char **argv)
{
	t_r01_puzzle		puzzle;

	if (argc != 2)
	{
		print_error();
		return (0);
	}
	parse_input_str(&puzzle, argv[1]);
	puzzle = r01_solve_puzzle(&puzzle);
	if (puzzle.is_invalid || !puzzle.is_complete)
	{
		print_error();
		return (0);
	}
	print_puzzle_grid(&puzzle);
	return (0);
}
