/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   work_instrumentation_micro_clock.c                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/22 19:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/22 19:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"
#include "search_timeout.h"

#if defined(WORK_INSTRUMENTED) && defined(WORK_MICRO_TIMING)

unsigned long long	work_micro_now(void)
{
	unsigned long long	now;

	if (search_timeout_cpu_nanoseconds(&now))
		return (now);
	return (0);
}

#endif
