/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   work_instrumentation_enabled.c                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"

#ifdef WORK_INSTRUMENTED

static unsigned long long	g_counts[WORK_COUNT];

void	work_dp_init(int size)
{
	work_add(WORK_DP_INIT_CALL, 1);
	work_add(WORK_DP_INIT_WRITE, 4 * (size + 1) * (size + 1)
		+ 2 + 2 * (size + 1));
}

void	work_reset(void)
{
	int	i;

	i = 0;
	while (i < WORK_COUNT)
		g_counts[i++] = 0;
	work_micro_reset();
}

void	work_add(t_work_counter counter, unsigned long long amount)
{
	if (counter >= 0 && counter < WORK_COUNT)
		g_counts[counter] += amount;
}

unsigned long long	work_get(t_work_counter counter)
{
	if (counter >= 0 && counter < WORK_COUNT)
		return (g_counts[counter]);
	return (0);
}

void	work_sort_shift(t_work_counter compare, t_work_counter shift)
{
	work_add(compare, 1);
	work_add(shift, 1);
}

#endif
