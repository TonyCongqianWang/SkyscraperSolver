/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 11:02:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/19 02:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"
#include <stdio.h>
#include <stdlib.h>

static void	partition_cache(t_puzzle *puzzle, t_node_order *cache,
				t_node_state *node)
{
	t_node_transition	tmp[MAX_CELL_COUNT];
	int					i;
	int					fill_c;
	int					emp_c;

	i = node->lowest_empty_idx;
	fill_c = i;
	emp_c = 0;
	while (i < cache->count)
	{
		if (!is_cell_empty(node, cache->entries[i].cell_idx))
			cache->entries[fill_c++] = cache->entries[i];
		else
			tmp[emp_c++] = cache->entries[i];
		i++;
	}
	i = -1;
	while (++i < emp_c)
		cache->entries[fill_c + i] = tmp[i];
	node->lowest_empty_idx = fill_c;
	(void)puzzle;
}

static void	rescore_empty_suffix(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config)
{
	t_node_state	*n;
	int				i;

	n = puzzle->cur_node;
	i = n->lowest_empty_idx;
	while (i < cache->count)
	{
		set_best_val_strat(puzzle, cache->entries[i].cell_idx,
			&cache->entries[i], config);
		i++;
	}
	sort_node_order(&cache->entries[n->lowest_empty_idx],
		cache->count - n->lowest_empty_idx, config->criterion);
}

static void	init_new_cache(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config, int old_top)
{
	t_node_state	*n;
	t_node_order	*parent_cache;

	n = puzzle->cur_node;
	parent_cache = &puzzle->order_stack.orders[old_top];
	if (old_top == 0 || parent_cache->build_depth < 0)
	{
		cache->count = 0;
		n->lowest_empty_idx = 0;
		cache->build_depth = n->cur_depth;
		collect_cache_entries(puzzle, cache, config);
		sort_node_order(cache->entries, cache->count, config->criterion);
	}
	else
	{
		*cache = *parent_cache;
		cache->build_depth = n->cur_depth;
		partition_cache(puzzle, cache, n);
		rescore_empty_suffix(puzzle, cache, config);
	}
}

static void	rebuild_existing_cache(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config)
{
	partition_cache(puzzle, cache, puzzle->cur_node);
	rescore_empty_suffix(puzzle, cache, config);
}

void	build_node_order(t_puzzle *puzzle, t_node_select_config *config)
{
	t_node_state	*n;
	t_node_order	*cache;
	int				top;

	n = puzzle->cur_node;
	cache = n->order_cache;
	top = puzzle->order_stack.top_idx;
	if (!cache || cache->build_depth < n->cur_depth)
	{
		puzzle->order_stack.top_idx++;
		if (puzzle->order_stack.top_idx >= MAX_STACK_DEPTH)
			exit(1);
		n->order_cache = &puzzle->order_stack
			.orders[puzzle->order_stack.top_idx];
		cache = n->order_cache;
		init_new_cache(puzzle, cache, config, top);
	}
	else
		rebuild_existing_cache(puzzle, cache, config);
	cache->last_build_entropy = n->remaining_entropy;
}
