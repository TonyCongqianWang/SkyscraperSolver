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

#if !defined(WORK_INSTRUMENTED) || !defined(WORK_MICRO_TIMING)

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
