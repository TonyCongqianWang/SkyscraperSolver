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

/* Version 1: add variable rescoring, resumption and domain scans. */
typedef enum e_work_counter
{
	WORK_SETUP_CELL,
	WORK_SETUP_CACHE_SLOT,
	WORK_CACHE_STATE_COPY,
	WORK_CACHE_PAIR_COPY,
	WORK_CACHE_PAIR_COPY_CALL,
	WORK_CACHE_BUILD_CANDIDATE,
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
	WORK_DP_CANDIDATE_CHECK,
	WORK_ASSIGNMENT,
	WORK_DOMAIN_INVALIDATION,
	WORK_NODE_COPY,
	WORK_LOOKAHEAD_SCAN,
	WORK_SOLUTION_COPY,
	WORK_PROVISIONAL_SOLUTION_ROLLBACK,
	WORK_RESCORE_SCAN,
	WORK_RESUME_SCAN,
	WORK_REL_ENTROPY_VALUE,
	WORK_DOMAIN_SCAN,
	WORK_CONSTRAINT_CHECK_CALL,
	WORK_CONSTRAINT_CHECK_CELL,
	WORK_CONSTRAINT_CHECK_UNSET_CELL,
	WORK_DIRTY_CONSTRAINT_ENTRY,
	WORK_DIRTY_CONSTRAINT_ENQUEUE,
	WORK_DOMAIN_INVALIDATION_ATTEMPT,
	WORK_CELL_BOUND_SKIP,
	WORK_CACHE_BUILD_CELL_SCAN,
	WORK_CACHE_NEXT_SCAN,
	WORK_CACHE_RESUME_SCAN,
	WORK_NEXT_VALUE_SCAN,
	WORK_PRUNE_LINE_SCAN,
	WORK_DP_PREFIX_CANDIDATE_SCAN,
	WORK_DP_SUFFIX_CANDIDATE_SCAN,
	WORK_DP_PRUNE_VALUE_SCAN,
	WORK_COUNT
}	t_work_counter;

void				work_micro_begin(t_work_counter counter);
void				work_micro_end(t_work_counter counter);
void				work_micro_reset(void);
void				work_micro_report(void);
void				work_dp_init(int size);
void				work_reset(void);
void				work_add(t_work_counter counter, unsigned long long amount);
void				work_sort_shift(t_work_counter compare,
						t_work_counter shift);
unsigned long long	work_get(t_work_counter counter);
void				work_report(unsigned long long solutions,
						unsigned long long nodes);

#endif
