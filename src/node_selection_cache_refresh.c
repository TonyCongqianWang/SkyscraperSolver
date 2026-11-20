/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_refresh.c                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "node_selection_score.h"
#include "line_order.h"

static int	refresh_due(t_node_state *node, t_node_select_config *config,
				t_order_refresh operation, int allow_stale)
{
	if (operation == ORDER_BLEND && node->order_cache->state.scores_dirty)
		return (1);
	if (!allow_stale)
		return (0);
	return (config->refresh_period[operation] <= 0
		|| node->order_cache->state.refresh_entropy[operation]
		- node->domain.remaining_entropy > config->refresh_period[operation]);
}

static void	refresh_part(t_node_state *node, t_order_refresh operation,
				t_selection_criterion criterion)
{
	t_node_order	*cache;

	cache = node->order_cache;
	if (operation == ORDER_COMPACT)
		compact_cache_entries(node, cache);
	else if (operation == ORDER_RESCORE)
		rescore_cache_entries(node, cache);
	else if (operation == ORDER_BLEND)
	{
		recalculate_cache_scores(node, cache);
		cache->state.scores_dirty = 0;
	}
	else if (operation == ORDER_SORT)
		sort_cached_orders(node, cache, criterion);
	else if (operation == ORDER_LINES)
		sort_line_order(node);
	cache->state.refresh_entropy[operation] = node->domain.remaining_entropy;
}

void	refresh_node_order(t_solver_state *puzzle,
			t_node_select_config *config, int allow_stale)
{
	int	i;

	i = -1;
	while (++i < ORDER_REFRESH_COUNT)
	{
		if (refresh_due(puzzle->cur_node, config, i, allow_stale))
		{
			isolate_node_order(puzzle);
			refresh_part(puzzle->cur_node, i, config->criterion);
		}
	}
}
