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

#define _POSIX_C_SOURCE 200809L
#include "work_instrumentation.h"

#if defined(WORK_INSTRUMENTED) && defined(WORK_MICRO_TIMING)
# include <time.h>

unsigned long long	work_micro_now(void)
{
	struct timespec	now;

	if (!clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &now))
		return ((unsigned long long)now.tv_sec * 1000000000ULL
			+ (unsigned long long)now.tv_nsec);
	return (0);
}

#endif
