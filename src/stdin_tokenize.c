/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stdin_tokenize.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/31 00:38:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "stdin_tokenize.h"

#include <string.h>

static int	tokenize_quoted(char **p, char **argv, int argc)
{
	(*p)++;
	argv[argc] = *p;
	while (**p && **p != '"')
		(*p)++;
	if (**p == '"')
	{
		**p = '\0';
		(*p)++;
	}
	return (argc + 1);
}

static int	tokenize_word(char **p, char **argv, int argc)
{
	argv[argc] = *p;
	while (**p && **p != ' ')
		(*p)++;
	if (**p == ' ')
	{
		**p = '\0';
		(*p)++;
	}
	return (argc + 1);
}

int	tokenize_line(char *line, char **argv, int max_args)
{
	int		argc;
	char	*p;

	argc = 0;
	p = line;
	while (*p && argc < max_args)
	{
		while (*p == ' ')
			p++;
		if (!*p)
			break ;
		if (*p == '"')
			argc = tokenize_quoted(&p, argv, argc);
		else
			argc = tokenize_word(&p, argv, argc);
	}
	return (argc);
}

int	has_stdin_flag(int argc, char **argv)
{
	int	i;

	i = 1;
	while (i < argc)
	{
		if (strcmp(argv[i], "--stdin") == 0)
			return (1);
		i++;
	}
	return (0);
}

char	*find_max_solutions_arg(int argc, char **argv)
{
	int	i;

	i = 1;
	while (i < argc - 1)
	{
		if (strcmp(argv[i], "-s") == 0)
			return (argv[i + 1]);
		i++;
	}
	return (NULL);
}
