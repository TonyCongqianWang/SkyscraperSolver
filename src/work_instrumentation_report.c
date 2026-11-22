/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   work_instrumentation_report.c             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"

#ifdef WORK_INSTRUMENTED
# include <stdio.h>

/* Frozen v1 counter names, in the order defined by the public enum. */
static const char	*g_names[WORK_COUNT] = {
	"setup_cell", "setup_cache_slot", "cache_state_copy",
	"cache_pair_copy", "cache_build_check", "compact_check",
	"compact_move", "transition_compare", "transition_shift",
	"line_copy", "line_score", "line_compare", "line_shift",
	"base_score", "lookahead_blend", "propagate_dp_update",
	"gac_check", "assignment", "domain_invalidation",
	"node_copy", "lookahead_scan", "solution_copy", "rollback"
};

void	work_report(unsigned long long solutions, unsigned long long nodes)
{
	int	i;

	printf("WORK_COUNTERS v1 solutions=%llu nodes=%llu", solutions, nodes);
	i = 0;
	while (i < WORK_COUNT)
	{
		printf(" %s=%llu", g_names[i], work_get(i));
		i++;
	}
	printf("\n");
}
#else
void	work_report(unsigned long long solutions, unsigned long long nodes)
{
	(void)solutions;
	(void)nodes;
}
#endif
