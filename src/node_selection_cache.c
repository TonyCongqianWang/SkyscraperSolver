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
#include "node_selection_score.h"
#include <stdio.h>
#include <stdlib.h>

static void	restore_lookahead_meta(t_node_order *cache,
				const t_node_transition *old_entries,
				const t_transition_meta *old_meta, int old_count)
{
	int	i;
	int	j;

	i = 0;
	while (i < cache->count)
	{
		j = 0;
		while (j < old_count)
		{
			if (old_entries[j].cell_idx == cache->entries[i].cell_idx
				&& old_entries[j].cell_val == cache->entries[i].cell_val)
			{
				cache->meta[i].entropy_pos = old_meta[j].entropy_pos;
				cache->meta[i].entropy_neg = old_meta[j].entropy_neg;
				break ;
			}
			j++;
		}
		i++;
	}
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
		cache->lookahead_build_entropy = -1;
		cache->needs_rebuild = 0;
		n->lowest_empty_idx = 0;
		cache->build_depth = n->cur_depth;
		collect_cache_entries(puzzle, cache, config);
		recalculate_cache_scores(n, cache);
		sort_node_order_meta(cache->entries, cache->meta,
			cache->count, config->criterion);
	}
	else
	{
		*cache = *parent_cache;
		cache->build_depth = n->cur_depth;
		compact_and_sort_cache(n, cache, config->criterion);
	}
}

static void	backup_cache(t_node_order *cache,
				t_node_transition *old_entries,
				t_transition_meta *old_meta, int *old_count)
{
	int	i;

	*old_count = cache->count;
	i = -1;
	while (++i < *old_count)
	{
		old_meta[i] = cache->meta[i];
		old_entries[i] = cache->entries[i];
	}
}

static void	rebuild_existing_cache(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config)
{
	t_transition_meta	old_meta[MAX_TRANSITIONS];
	t_node_transition	old_entries[MAX_TRANSITIONS];
	int					old_count;
	int					old_lh_entropy;

	old_lh_entropy = cache->lookahead_build_entropy;
	backup_cache(cache, old_entries, old_meta, &old_count);
	cache->build_depth = puzzle->cur_node->cur_depth;
	collect_cache_entries(puzzle, cache, config);
	cache->lookahead_build_entropy = old_lh_entropy;
	cache->needs_rebuild = 0;
	restore_lookahead_meta(cache, old_entries, old_meta, old_count);
	recalculate_cache_scores(puzzle->cur_node, cache);
	sort_node_order_meta(cache->entries, cache->meta,
		cache->count, config->criterion);
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
