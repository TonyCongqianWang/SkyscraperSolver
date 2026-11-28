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

#include "work_instrumentation.h"
#include "print_io.h"
#include "puzzle_structs.h"
#include "puzzle_solver.h"
#include "solution_storage.h"
#include "argument_parsing.h"
#include "stdin_mode.h"
#include "stdin_tokenize.h"

int	main(int argc, char **argv)
{
	static t_solver_state	puzzle;
	int						parsing_retcode;

	if (has_stdin_flag(argc, argv))
		return (run_stdin_mode(argc, argv));
	work_reset();
	parsing_retcode = init_puzzle_from_argv(&puzzle, argc, argv);
	if (parsing_retcode != 0)
	{
		free_solution_storage(&puzzle);
		return (parsing_retcode);
	}
	solve_puzzle(&puzzle, -1);
	print_solver_result(&puzzle);
	free_solution_storage(&puzzle);
	return (0);
}
