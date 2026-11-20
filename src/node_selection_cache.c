/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache.c                        :+:      :+:    :+:   */
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
#include <stdlib.h>

void	isolate_node_order(t_solver_state *puzzle)
{
	t_node_state	*n;
	t_node_order	*parent;
	int				idx;

	n = puzzle->cur_node;
	parent = n->order_cache;
	if (parent->state.build_depth == n->tree.depth)
		return ;
	idx = parent - puzzle->order_stack.orders;
	if (++puzzle->order_stack.top_idx >= MAX_STACK_DEPTH)
		exit(1);
	n->order_cache = &puzzle->order_stack
		.orders[puzzle->order_stack.top_idx];
	copy_node_order(n->order_cache, parent);
	n->order_cache->state.build_depth = n->tree.depth;
	copy_line_order(puzzle, idx);
}

void	build_node_order(t_solver_state *puzzle, t_node_select_config *config)
{
	t_node_state	*node;
	t_node_order	*cache;
	int				i;

	isolate_node_order(puzzle);
	node = puzzle->cur_node;
	cache = node->order_cache;
	if (cache->state.refresh_entropy[ORDER_COMPACT] < 0)
		collect_cache_entries(puzzle, cache, config);
	else
		compact_cache_entries(node, cache);
	rescore_cache_entries(node, cache);
	recalculate_cache_scores(node, cache);
	sort_cached_orders(node, cache, config->criterion);
	sort_line_order(node);
	cache->state.scores_dirty = 0;
	i = -1;
	while (++i < ORDER_REFRESH_COUNT)
		cache->state.refresh_entropy[i] = node->domain.remaining_entropy;
}
