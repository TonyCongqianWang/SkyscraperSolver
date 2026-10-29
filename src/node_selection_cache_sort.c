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
#include "line_order.h"

void	sort_cached_orders(t_node_state *node, t_node_order *cache,
			t_selection_criterion criterion)
{
	sort_node_order_meta(cache->entries, cache->meta, cache->count, criterion);
	sort_line_order(node);
}
