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
				t_node_state *node, int sf_idx)
{
	t_node_transition	tmp[MAX_CELL_COUNT];
	int					i;
	int					fill_c;
	int					emp_c;

	i = node->lowest_empty_idx[sf_idx];
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
	node->lowest_empty_idx[sf_idx] = fill_c;
	(void)puzzle;
}

static void	rescore_empty_suffix(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config, int sf)
{
	t_node_state	*n;
	int				i;

	n = puzzle->cur_node;
	i = n->lowest_empty_idx[sf];
	while (i < cache->count)
	{
		set_best_val_strat(puzzle, cache->entries[i].cell_idx,
			&cache->entries[i], config);
		i++;
	}
	sort_node_order(&cache->entries[n->lowest_empty_idx[sf]],
		cache->count - n->lowest_empty_idx[sf], config->criterion);
}

static void	init_new_cache(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config, int sf, int old_top)
{
	t_node_state	*n;
	t_node_order	*parent_cache;

	n = puzzle->cur_node;
	parent_cache = &puzzle->order_stacks.stacks[sf].orders[old_top];
	if (old_top == 0 || parent_cache->build_depth < 0)
	{
		cache->count = 0;
		n->lowest_empty_idx[sf] = 0;
		cache->build_depth = n->cur_depth;
		collect_cache_entries(puzzle, cache, config);
		sort_node_order(cache->entries, cache->count, config->criterion);
	}
	else
	{
		*cache = *parent_cache;
		cache->build_depth = n->cur_depth;
		partition_cache(puzzle, cache, n, sf);
		rescore_empty_suffix(puzzle, cache, config, sf);
	}
}

static void	rebuild_existing_cache(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config, int sf)
{
	partition_cache(puzzle, cache, puzzle->cur_node, sf);
	rescore_empty_suffix(puzzle, cache, config, sf);
}

void	build_node_order(t_puzzle *puzzle, t_node_select_config *config)
{
	t_node_state	*n;
	t_node_order	*cache;
	int				sf;
	int				top;

	n = puzzle->cur_node;
	sf = get_score_family_idx(config->score_family);
	cache = n->order_caches[sf];
	top = puzzle->order_stacks.stacks[sf].top_idx;
	if (!cache || cache->build_depth < n->cur_depth)
	{
		puzzle->order_stacks.stacks[sf].top_idx++;
		if (puzzle->order_stacks.stacks[sf].top_idx >= MAX_STACK_DEPTH)
			exit(1);
		n->order_caches[sf] = &puzzle->order_stacks
			.stacks[sf].orders[puzzle->order_stacks.stacks[sf].top_idx];
		cache = n->order_caches[sf];
		init_new_cache(puzzle, cache, config, sf, top);
	}
	else
		rebuild_existing_cache(puzzle, cache, config, sf);
	cache->last_build_prog = n->progress_counter;
}

void	rebuild_cache_if_stale(t_puzzle *puzzle,
			t_node_select_config *config, int allow_stale_rebuild)
{
	t_node_state	*node;
	t_node_order	*cache;
	int				sf;
	int				is_stale;

	node = puzzle->cur_node;
	sf = get_score_family_idx(config->score_family);
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
	int				sf;

	sf = get_score_family_idx(config->score_family);
	cache = puzzle->cur_node->order_caches[sf];
	i = puzzle->cur_node->lowest_empty_idx[sf];
	while (i < cache->count)
	{
		if (is_cell_empty(puzzle->cur_node, cache->entries[i].cell_idx)
			&& check_sel_filter(puzzle->cur_node, cache->entries[i].cell_idx,
				puzzle->size, config->is_selective))
		{
			if (try_cached_entry(puzzle, next, cache, i))
				return (1);
		}
		i++;
	}
	return (0);
}

int	get_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	int	i;
	int	sf;

	sf = get_score_family_idx(config->score_family);
	if (resume_next_from_cache(puzzle, next, sf, &i))
		return (1);
	while (i < puzzle->cur_node->order_caches[sf]->count)
	{
		next->cell_idx = puzzle->cur_node->order_caches[sf]->entries[i].cell_idx;
		next->cell_val = 1;
		if (is_cell_empty(puzzle->cur_node, next->cell_idx) && check_sel_filter(
				puzzle->cur_node, next->cell_idx, puzzle->size, config->is_selective)
			&& set_next_valid_val(puzzle, next)
			&& is_cell_empty(puzzle->cur_node, next->cell_idx))
			return (1);
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
