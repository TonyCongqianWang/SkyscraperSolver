/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_sort.c                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:40:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:40:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_eval.h"

void	sort_cached_orders(t_node_state *node, t_node_order *cache,
			t_selection_criterion criterion)
{
	if (cache->state.order_dirty || cache->state.order_criterion != criterion)
	{
		if (cache->items.count > 1)
			sort_node_order_meta(cache->items.entries, cache->items.meta,
				cache->items.count,
				criterion);
		cache->state.order_dirty = 0;
		cache->state.order_criterion = criterion;
	}
	(void)node;
}
