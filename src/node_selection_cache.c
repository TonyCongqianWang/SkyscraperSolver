/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 11:02:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 16:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"
#include <stdio.h>
#include <stdlib.h>

static void	collect_cache_entries(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config)
{
	int					cell_idx;
	t_node_transition	best;

	cell_idx = 0;
	while (cell_idx < puzzle->squared_size)
	{
		if (is_cell_empty(puzzle->cur_node, cell_idx))
		{
			set_best_val_strat(puzzle, cell_idx, &best, config);
			if (best.cell_idx != -1)
			{
				cache->entries[cache->count] = best;
				cache->count++;
			}
		}
		cell_idx++;
	}
}

void	build_node_order(t_puzzle *puzzle, t_node_select_config *config)
{
	t_node_state		*node;
	t_node_order		*cache;
	int					sf_idx;
	int					top;

	node = puzzle->cur_node;
	sf_idx = get_score_family_idx(config->score_family);
	cache = node->order_caches[sf_idx];
	if (!cache || cache->build_depth < node->cur_depth)
	{
		puzzle->order_stacks.stacks[sf_idx].top_idx++;
		top = puzzle->order_stacks.stacks[sf_idx].top_idx;
		if (top >= MAX_STACK_DEPTH)
			exit(1);
		node->order_caches[sf_idx] = &puzzle->order_stacks
			.stacks[sf_idx].orders[top];
		cache = node->order_caches[sf_idx];
	}
	cache->count = 0;
	node->lowest_valid_idx[sf_idx] = 0;
	cache->build_depth = node->cur_depth;
	collect_cache_entries(puzzle, cache, config);
	sort_node_order(cache->entries, cache->count, config->criterion);
	cache->last_build_prog = node->progress_counter;
}

void	rebuild_cache_if_stale(t_puzzle *puzzle,
			t_node_select_config *config, int allow_stale_rebuild)
{
	t_node_state	*node;
	t_node_order	*cache;
	int				sf;
	int				is_stale;

	node = puzzle->cur_node;
	sf = config->score_family;
	cache = node->order_caches[sf];
	if (cache->last_build_prog == 0)
		is_stale = 1;
	else if (!allow_stale_rebuild)
		is_stale = 0;
	else
		is_stale = (node->progress_counter
				>= cache->last_build_prog + config->rebuild_period);
	if (is_stale)
		build_node_order(puzzle, config);
}

int	get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_order	*cache;
	int				i;
	int				sf_idx;
	int				cell;

	sf_idx = get_score_family_idx(config->score_family);
	cache = puzzle->cur_node->order_caches[sf_idx];
	i = puzzle->cur_node->lowest_valid_idx[sf_idx];
	while (i < cache->count)
	{
		cell = cache->entries[i].cell_idx;
		if (is_cell_empty(puzzle->cur_node, cell)
			&& check_sel_filter(puzzle->cur_node, cell, puzzle->size,
				config->is_selective))
		{
			if (try_cached_entry(puzzle, next, cache, i))
				return (1);
		}
		if (i == puzzle->cur_node->lowest_valid_idx[sf_idx])
			puzzle->cur_node->lowest_valid_idx[sf_idx]++;
		i++;
	}
	return (0);
}

int	get_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_order	*cache;
	int				i;
	int				sf_idx;

	sf_idx = get_score_family_idx(config->score_family);
	cache = puzzle->cur_node->order_caches[sf_idx];
	if (resume_next_from_cache(puzzle, next, sf_idx, &i))
		return (1);
	while (i < cache->count)
	{
		if (process_next_entry(puzzle, next, config, i))
			return (1);
		if (!puzzle->cur_node->is_in_lookahead_select
			&& i == puzzle->cur_node->lowest_valid_idx[sf_idx])
			puzzle->cur_node->lowest_valid_idx[sf_idx]++;
		i++;
	}
	return (0);
}

void	init_order_stacks(t_puzzle *puzzle)
{
	int				sf;
	int				stack_idx;
	t_node_order	*order;

	sf = 0;
	while (sf < 3)
	{
		puzzle->order_stacks.stacks[sf].top_idx = 0;
		stack_idx = 0;
		while (stack_idx < MAX_STACK_DEPTH)
		{
			order = &puzzle->order_stacks.stacks[sf].orders[stack_idx];
			order->last_build_prog = 0;
			order->build_depth = -1;
			stack_idx++;
		}
		sf++;
	}
}
