/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 11:03:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

void	build_node_order(t_puzzle *puzzle, t_node_select_config *config)
{
	t_node_state		*node;
	t_node_order		*cache;
	int					cell_idx;
	t_node_transition	best;

	node = puzzle->cur_node;
	cache = &node->order_caches[get_cache_index(node)];
	cache->count = 0;
	cache->lowest_valid_idx = 0;
	cell_idx = 0;
	while (cell_idx < puzzle->squared_size)
	{
		if (is_cell_empty(node, cell_idx))
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
	sort_node_order(cache->entries, cache->count, config->criterion);
	cache->last_build_prog = node->progress_counter;
}

void	rebuild_cache_if_stale(t_puzzle *puzzle, t_node_order *cache,
			t_node_select_config *config)
{
	t_node_state	*node;

	node = puzzle->cur_node;
	if (cache->last_build_prog == 0
		|| (!node->is_in_lookahead_select
			&& node->progress_counter
			>= cache->last_build_prog + config->rebuild_period))
		build_node_order(puzzle, config);
}

int	get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_order	*cache;
	int				i;

	cache = &puzzle->cur_node->order_caches[get_cache_index(puzzle->cur_node)];
	i = cache->lowest_valid_idx;
	while (i < cache->count)
	{
		if (is_cell_empty(puzzle->cur_node, cache->entries[i].cell_idx)
			&& is_valid_value(puzzle->cur_node, cache->entries[i].cell_idx,
				cache->entries[i].cell_val)
			&& check_sel_filter(puzzle->cur_node, cache->entries[i].cell_idx,
				puzzle->size, config->is_selective))
		{
			*next = cache->entries[i];
			return (1);
		}
		if (i == cache->lowest_valid_idx)
			cache->lowest_valid_idx++;
		i++;
	}
	return (0);
}

int	get_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_order	*cache;
	int				i;

	cache = &puzzle->cur_node->order_caches[get_cache_index(puzzle->cur_node)];
	if (resume_next_from_cache(puzzle, next, cache, &i))
		return (1);
	while (i < cache->count)
	{
		if (is_cell_empty(puzzle->cur_node, cache->entries[i].cell_idx)
			&& check_sel_filter(puzzle->cur_node, cache->entries[i].cell_idx,
				puzzle->size, config->is_selective))
		{
			next->cell_idx = cache->entries[i].cell_idx;
			next->cell_val = 1;
			if (set_next_valid_val(puzzle, next)
				&& is_cell_empty(puzzle->cur_node, next->cell_idx))
				return (1);
		}
		if (i == cache->lowest_valid_idx)
			cache->lowest_valid_idx++;
		i++;
	}
	return (0);
}
