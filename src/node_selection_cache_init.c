/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_init.c                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"
#include "node_selection_cache.h"

void	init_order_stacks(t_solver_state *puzzle)
{
	int				stack_idx;
	int				i;
	t_node_order	*order;

	puzzle->order_stack.top_idx = 0;
	stack_idx = -1;
	while (++stack_idx < MAX_STACK_DEPTH)
	{
		order = &puzzle->order_stack.orders[stack_idx];
		order->items.count = 0;
		order->state.lookahead_build_entropy = -1;
		order->state.scores_dirty = 0;
		order->state.order_dirty = 0;
		order->state.order_criterion = SELECT_MAX;
		order->state.build_depth = -1;
		i = -1;
		while (++i < ORDER_REFRESH_COUNT)
			order->state.refresh_entropy[i] = -1;
		work_add(WORK_SETUP_CACHE_SLOT, 1);
	}
}

void	rebuild_cache_if_stale(t_solver_state *puzzle,
			t_node_select_config *config, int allow_stale_rebuild)
{
	t_node_order	*cache;

	cache = puzzle->cur_node->order_cache;
	if (cache->state.refresh_entropy[ORDER_COMPACT] < 0)
		build_node_order(puzzle, config);
	else
		refresh_node_order(puzzle, config, allow_stale_rebuild);
}
