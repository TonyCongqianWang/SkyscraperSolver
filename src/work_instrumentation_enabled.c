#include "work_instrumentation.h"

#ifdef WORK_INSTRUMENTED

static unsigned long long	g_counts[WORK_COUNT];

void	work_reset(void)
{
	int	i;

	i = 0;
	while (i < WORK_COUNT)
		g_counts[i++] = 0;
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
