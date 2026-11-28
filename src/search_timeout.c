/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_timeout.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/27 18:21:38 by towang            #+#    #+#             */
/*   Updated: 2026/11/28 13:37:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "search_timeout.h"
#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static double		g_deadline;
static t_node_count	g_limit;
static t_node_count	g_last;
static int			g_report;
static int			g_stopped;
static int			g_cpu_mode;

static void	invalid_setting(void)
{
	fprintf(stderr,
		"Invalid search timeout configuration or CPU clock failure\n");
	exit(EXIT_FAILURE);
}

static void	init_cpu_timeout(const char *cpu)
{
	char	*end;
	double	seconds;
	double	now;

	errno = 0;
	seconds = strtod(cpu, &end);
	if (errno || end == cpu || *end || !isfinite(seconds) || seconds <= 0)
		invalid_setting();
	now = search_timeout_cpu_seconds();
	if (now < 0 || !isfinite(now + seconds))
		invalid_setting();
	g_deadline = now + seconds;
	g_cpu_mode = 1;
}

void	search_timeout_init(void)
{
	const char	*cpu;
	const char	*limit;
	char		*end;

	cpu = getenv("SOLVER_CPU_TIMEOUT");
	limit = getenv("SOLVER_MAIN_NODE_LIMIT");
	g_deadline = 0;
	g_limit = 0;
	g_last = 0;
	g_stopped = 0;
	g_cpu_mode = 0;
	g_report = getenv("SOLVER_SEARCH_STATUS") != NULL || cpu || limit;
	if (cpu && limit)
		invalid_setting();
	if (cpu)
		init_cpu_timeout(cpu);
	if (limit)
	{
		errno = 0;
		g_limit = strtoull(limit, &end, 10);
		if (errno || *limit < '0' || *limit > '9' || *end || !g_limit)
			invalid_setting();
	}
}

int	search_timeout_check(t_node_count main_nodes)
{
	double	now;

	if (!g_cpu_mode && !g_limit)
		return (0);
	if (main_nodes == g_last)
		return (0);
	g_last = main_nodes;
	if (g_cpu_mode)
	{
		now = search_timeout_cpu_seconds();
		if (now < 0)
			invalid_setting();
		g_stopped = (now >= g_deadline);
	}
	else
		g_stopped = (main_nodes >= g_limit);
	return (g_stopped);
}

void	search_timeout_report(void)
{
	if (!g_report)
		return ;
	if (g_stopped)
		printf("SEARCH_STATUS timeout\n");
	else
		printf("SEARCH_STATUS complete\n");
}
