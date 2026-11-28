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

static unsigned long long	filetime_ticks(FILETIME time)
{
	ULARGE_INTEGER	value;

	value.LowPart = time.dwLowDateTime;
	value.HighPart = time.dwHighDateTime;
	return (value.QuadPart);
}

int	search_timeout_cpu_nanoseconds(unsigned long long *ns)
{
	FILETIME	creation;
	FILETIME	exit_time;
	FILETIME	kernel;
	FILETIME	user;

	if (!GetProcessTimes(GetCurrentProcess(), &creation, &exit_time,
			&kernel, &user))
		return (0);
	*ns = (filetime_ticks(kernel) + filetime_ticks(user)) * 100ULL;
	return (1);
}

#else

int	search_timeout_cpu_nanoseconds(unsigned long long *ns)
{
	struct timespec	now;

	if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &now))
		return (0);
	*ns = (unsigned long long)now.tv_sec * 1000000000ULL
		+ (unsigned long long)now.tv_nsec;
	return (1);
}

#endif

double	search_timeout_cpu_seconds(void)
{
	unsigned long long	ns;

	if (!search_timeout_cpu_nanoseconds(&ns))
		return (-1.0);
	return ((double)ns / 1e9);
}
