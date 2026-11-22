/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   work_instrumentation_disabled.c                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"

#ifndef WORK_INSTRUMENTED

void	work_dp_init(int size)
{
	(void)size;
}

void	work_reset(void)
{
}

void	work_add(t_work_counter counter, unsigned long long amount)
{
	(void)counter;
	(void)amount;
}

unsigned long long	work_get(t_work_counter counter)
{
	(void)counter;
	return (0);
}

void	work_sort_shift(t_work_counter compare, t_work_counter shift)
{
	(void)compare;
	(void)shift;
}

#endif
