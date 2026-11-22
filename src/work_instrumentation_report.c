/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   work_instrumentation_report.c                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"

#ifdef WORK_INSTRUMENTED
# include <stdio.h>

/* Frozen v2 counter names, in the order defined by the public enum. */
static const char	*g_names[WORK_COUNT] = {
	"setup_cell", "setup_cache_slot", "cache_state_copy",
	"cache_pair_copy", "cache_pair_copy_call", "cache_build_check",
	"compact_check",
	"compact_move", "transition_compare", "transition_shift",
	"line_copy", "line_score", "line_score_value",
	"line_compare", "line_shift",
	"base_score", "lookahead_blend", "propagate_dp_update",
	"dp_init_call", "dp_init_write", "index_copy_call", "index_copy_pair",
	"gac_check", "assignment", "domain_invalidation",
	"node_copy", "lookahead_scan", "solution_copy", "rollback"
};

void	work_report(unsigned long long solutions, unsigned long long nodes)
{
	int	i;

	printf("WORK_COUNTERS v2 solutions=%llu nodes=%llu", solutions, nodes);
	i = 0;
	while (i < WORK_COUNT)
	{
		printf(" %s=%llu", g_names[i], work_get(i));
		i++;
	}
	printf("\n");
	work_micro_report();
}

#else

void	work_report(unsigned long long solutions, unsigned long long nodes)
{
	(void)solutions;
	(void)nodes;
}
#endif
