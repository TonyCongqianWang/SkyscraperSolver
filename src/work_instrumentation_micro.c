/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   work_instrumentation_micro.c                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/22 19:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/22 19:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"

#if defined(WORK_INSTRUMENTED) && defined(WORK_MICRO_TIMING)
# include <time.h>
# include <stdio.h>

static clock_t				g_starts[WORK_COUNT];
static unsigned long long	g_calls[WORK_COUNT];
static unsigned long long	g_samples[WORK_COUNT];
static unsigned long long	g_ticks[WORK_COUNT];
static int					g_active[WORK_COUNT];

void	work_micro_begin(t_work_counter counter)
{
	if (counter < 0 || counter >= WORK_COUNT)
		return ;
	g_calls[counter]++;
	if (g_calls[counter] % 64 != 0 || g_active[counter])
		return ;
	g_starts[counter] = clock();
	g_active[counter] = 1;
}

void	work_micro_end(t_work_counter counter)
{
	clock_t	end;

	if (counter < 0 || counter >= WORK_COUNT || !g_active[counter])
		return ;
	end = clock();
	if (end >= g_starts[counter])
		g_ticks[counter] += (unsigned long long)(end - g_starts[counter]);
	g_samples[counter]++;
	g_active[counter] = 0;
}

void	work_micro_reset(void)
{
	int	i;

	i = -1;
	while (++i < WORK_COUNT)
	{
		g_calls[i] = 0;
		g_samples[i] = 0;
		g_ticks[i] = 0;
		g_active[i] = 0;
	}
}

void	work_micro_report(void)
{
	int	i;

	i = -1;
	while (++i < WORK_COUNT)
	{
		if (!g_samples[i])
			continue ;
		printf("WORK_MICRO v1 counter=%d calls=%llu samples=%llu ticks=%llu"
			" clock_ticks_per_second=%ld\n",
			i, g_calls[i], g_samples[i], g_ticks[i],
			(long)CLOCKS_PER_SEC);
	}
}

#else

void	work_micro_begin(t_work_counter counter)
{
	(void)counter;
}

void	work_micro_end(t_work_counter counter)
{
	(void)counter;
}

void	work_micro_reset(void)
{
}

void	work_micro_report(void)
{
}

#endif
