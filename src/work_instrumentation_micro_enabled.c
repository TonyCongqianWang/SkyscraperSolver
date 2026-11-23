/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   work_instrumentation_micro_enabled.c               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/22 19:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/22 19:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"

#if defined(WORK_INSTRUMENTED) && defined(WORK_MICRO_TIMING)
# include <stdio.h>

static unsigned long long	g_starts[WORK_COUNT];
static unsigned long long	g_calls[WORK_COUNT];
static unsigned long long	g_samples[WORK_COUNT];
static unsigned long long	g_ticks[WORK_COUNT];
static unsigned long long	g_vol_starts[WORK_COUNT];
static unsigned long long	g_volumes[WORK_COUNT];
static int					g_active[WORK_COUNT];

unsigned long long	work_micro_now(void);

static t_work_counter	work_micro_volume(t_work_counter counter)
{
	if (counter == WORK_CACHE_PAIR_COPY_CALL)
		return (WORK_CACHE_PAIR_COPY);
	if (counter == WORK_LINE_SCORE)
		return (WORK_LINE_SCORE_VALUE);
	if (counter == WORK_INDEX_COPY_CALL)
		return (WORK_INDEX_COPY_PAIR);
	return (WORK_COUNT);
}

void	work_micro_begin(t_work_counter counter)
{
	t_work_counter	volume;

	if (counter < 0 || counter >= WORK_COUNT)
		return ;
	g_calls[counter]++;
	if (g_calls[counter] % 64 != 0 || g_active[counter])
		return ;
	volume = work_micro_volume(counter);
	if (volume != WORK_COUNT)
		g_vol_starts[counter] = work_get(volume);
	g_starts[counter] = work_micro_now();
	g_active[counter] = 1;
}

void	work_micro_end(t_work_counter counter)
{
	unsigned long long	end;
	t_work_counter		volume;

	if (counter < 0 || counter >= WORK_COUNT || !g_active[counter])
		return ;
	end = work_micro_now();
	volume = work_micro_volume(counter);
	if (end >= g_starts[counter])
		g_ticks[counter] += end - g_starts[counter];
	if (volume != WORK_COUNT)
		g_volumes[counter] += work_get(volume) - g_vol_starts[counter];
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
		g_volumes[i] = 0;
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
		printf("WORK_MICRO v1 counter=%d calls=%llu samples=%llu"
			" ticks=%llu clock_ticks_per_second=1000000000"
			" sampled_volume=%llu\n",
			i, g_calls[i], g_samples[i], g_ticks[i],
			g_volumes[i]);
	}
}

#endif
