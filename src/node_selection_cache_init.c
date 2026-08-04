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

#include "node_selection_cache.h"

void	init_order_stacks(t_puzzle *puzzle)
{
	int				stack_idx;
	t_node_order	*order;

	puzzle->order_stack.top_idx = 0;
	stack_idx = 0;
	while (stack_idx < MAX_STACK_DEPTH)
	{
		order = &puzzle->order_stack.orders[stack_idx];
		order->last_build_entropy = -1;
		order->lookahead_build_entropy = -1;
		order->needs_rebuild = 0;
		order->build_depth = -1;
		stack_idx++;
	}
}

void	rebuild_cache_if_stale(t_puzzle *puzzle,
			t_node_select_config *config, int allow_stale_rebuild)
{
	t_node_state	*node;
	t_node_order	*cache;
	int				is_stale;

	node = puzzle->cur_node;
	cache = node->order_cache;
	if (cache->needs_rebuild || cache->last_build_entropy == -1)
		is_stale = 1;
	else if (!allow_stale_rebuild)
		is_stale = 0;
	else
		is_stale = (cache->last_build_entropy - node->remaining_entropy
				> config->rebuild_period);
	if (is_stale)
		build_node_order(puzzle, config);
}
