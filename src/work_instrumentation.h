/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   work_instrumentation.h                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef WORK_INSTRUMENTATION_H
# define WORK_INSTRUMENTATION_H

/* Version 2: calls and real variable work volumes are distinct units. */
typedef enum e_work_counter
{
	WORK_SETUP_CELL,
	WORK_SETUP_CACHE_SLOT,
	WORK_CACHE_STATE_COPY,
	WORK_CACHE_PAIR_COPY,
	WORK_CACHE_PAIR_COPY_CALL,
	WORK_CACHE_BUILD_CHECK,
	WORK_COMPACT_CHECK,
	WORK_COMPACT_MOVE,
	WORK_TRANSITION_COMPARE,
	WORK_TRANSITION_SHIFT,
	WORK_LINE_COPY,
	WORK_LINE_SCORE,
	WORK_LINE_SCORE_VALUE,
	WORK_LINE_COMPARE,
	WORK_LINE_SHIFT,
	WORK_BASE_SCORE,
	WORK_LOOKAHEAD_BLEND,
	WORK_PROPAGATE_DP_UPDATE,
	WORK_DP_INIT_CALL,
	WORK_DP_INIT_WRITE,
	WORK_INDEX_COPY_CALL,
	WORK_INDEX_COPY_PAIR,
	WORK_GAC_CHECK,
	WORK_ASSIGNMENT,
	WORK_DOMAIN_INVALIDATION,
	WORK_NODE_COPY,
	WORK_LOOKAHEAD_SCAN,
	WORK_SOLUTION_COPY,
	WORK_ROLLBACK,
	WORK_COUNT
}	t_work_counter;

void				work_reset(void);
void				work_add(t_work_counter counter, unsigned long long amount);
void				work_sort_shift(t_work_counter compare,
						t_work_counter shift);
unsigned long long	work_get(t_work_counter counter);
void				work_report(unsigned long long solutions,
						unsigned long long nodes);

#endif
