/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_copy.c                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:40:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:40:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"
#include "node_selection_cache.h"

void	copy_order_items(t_order_items *target, const t_order_items *source)
{
	int	i;

	work_micro_begin(WORK_CACHE_PAIR_COPY_CALL);
	work_add(WORK_CACHE_PAIR_COPY_CALL, 1);
	work_add(WORK_CACHE_PAIR_COPY, source->count);
	target->count = source->count;
	i = -1;
	while (++i < source->count)
	{
		target->entries[i] = source->entries[i];
		target->meta[i] = source->meta[i];
	}
	work_micro_end(WORK_CACHE_PAIR_COPY_CALL);
}

void	copy_node_order(t_node_order *target, const t_node_order *source)
{
	work_micro_begin(WORK_CACHE_STATE_COPY);
	work_add(WORK_CACHE_STATE_COPY, 1);
	target->state = source->state;
	work_micro_end(WORK_CACHE_STATE_COPY);
	copy_order_items(&target->items, &source->items);
}
