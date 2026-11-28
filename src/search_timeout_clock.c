/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_timeout_clock.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/27 18:21:38 by towang            #+#    #+#             */
/*   Updated: 2026/11/28 13:37:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#define _POSIX_C_SOURCE 200809L
#include "search_timeout.h"
#ifdef _WIN32
# include <windows.h>
#else
# include <time.h>
#endif

#ifdef _WIN32

static double	filetime_ticks(FILETIME time)
{
	ULARGE_INTEGER	value;

	value.LowPart = time.dwLowDateTime;
	value.HighPart = time.dwHighDateTime;
	return ((double)value.QuadPart);
}

double	search_timeout_cpu_seconds(void)
{
	FILETIME	creation;
	FILETIME	exit_time;
	FILETIME	kernel;
	FILETIME	user;

	if (!GetProcessTimes(GetCurrentProcess(), &creation, &exit_time,
			&kernel, &user))
		return (-1.0);
	return ((filetime_ticks(kernel) + filetime_ticks(user)) / 10000000.0);
}

#else

double	search_timeout_cpu_seconds(void)
{
	struct timespec	now;

	if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &now))
		return (-1.0);
	return ((double)now.tv_sec + (double)now.tv_nsec / 1e9);
}

#endif
