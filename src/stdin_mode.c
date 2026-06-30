/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stdin_mode.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/31 00:38:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "stdin_mode.h"
#include "stdin_tokenize.h"
#include "print_io.h"
#include "puzzle_structs.h"
#include "puzzle_solver.h"
#include "solution_storage.h"
#include "argument_parsing.h"

#include <string.h>
#include <stdio.h>

static void	process_stdin_instance(t_puzzle *puzzle, int argc, char **argv)
{
	memset(puzzle, 0, sizeof(*puzzle));
	if (init_puzzle_from_argv(puzzle, argc, argv) != 0)
	{
		print_error("Wrong puzzle constraints format.");
		printf("--- END_OF_INSTANCE ---\n");
		fflush(stdout);
		free_solution_storage(puzzle);
		return ;
	}
	solve_puzzle(puzzle, -1);
	print_value("Nodes visited", puzzle->nodes_visited);
	printf("--- END_OF_INSTANCE ---\n");
	fflush(stdout);
	free_solution_storage(puzzle);
}

static int	build_fake_argv(char **fake_argv, char *prog,
		char *max_solutions, char *line)
{
	int	fake_argc;
	int	max_cli;

	fake_argc = 0;
	fake_argv[fake_argc++] = prog;
	if (max_solutions)
	{
		fake_argv[fake_argc++] = "-s";
		fake_argv[fake_argc++] = max_solutions;
	}
	max_cli = (MAX_CLI_ARGS + 1) - fake_argc;
	fake_argc += tokenize_line(line, &fake_argv[fake_argc], max_cli);
	return (fake_argc);
}

static int	read_and_strip_line(char *line, int size)
{
	size_t	len;

	if (!fgets(line, size, stdin))
		return (0);
	len = strlen(line);
	if (len > 0 && line[len - 1] == '\n')
		line[len - 1] = '\0';
	if (strlen(line) == 0)
		return (-1);
	return (1);
}

int	run_stdin_mode(int argc, char **argv)
{
	static t_puzzle	puzzle;
	char			*max_solutions;
	char			line[4096];
	char			*fake_argv[MAX_CLI_ARGS + 1];
	int				ret;

	max_solutions = find_max_solutions_arg(argc, argv);
	while (1)
	{
		ret = read_and_strip_line(line, sizeof(line));
		if (ret == 0)
			break ;
		if (ret == -1)
			continue ;
		memset(fake_argv, 0, sizeof(fake_argv));
		ret = build_fake_argv(fake_argv, argv[0], max_solutions,
				line);
		process_stdin_instance(&puzzle, ret, fake_argv);
	}
	return (0);
}
