/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 10:40:00 by towang           ###   ########.fr       */
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

#ifndef REBUILD_IN_LOOKAHEAD
# define REBUILD_IN_LOOKAHEAD 0
#endif

static int	check_selective_filter(t_node_state *node, int cell_idx,
				int size, int is_selective)
{
	if (!node->is_in_lookahead_select || !is_selective)
		return (1);
	return ((node->rows_changed_since_prune & (1 << (cell_idx / size)))
		|| (node->cols_changed_since_prune & (1 << (cell_idx % size))));
}

static void	rebuild_cache_if_stale(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config)
{
	t_node_state	*node;

	node = puzzle->cur_node;
	if (cache->last_build_prog == 0
		|| ((REBUILD_IN_LOOKAHEAD || !node->is_in_lookahead_select)
			&& node->progress_counter
			>= cache->last_build_prog + config->rebuild_period))
		build_node_order(puzzle, config);
}

static int	resume_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
				t_node_order *cache, int *i_out)
{
	int	i;

	if (next->cell_idx < 0)
	{
		*i_out = cache->lowest_valid_idx;
		return (0);
	}
	i = cache->lowest_valid_idx;
	while (i < cache->count && cache->entries[i].cell_idx != next->cell_idx)
		i++;
	if (i < cache->count)
	{
		next->cell_val++;
		if (set_next_valid_val(puzzle, next)
			&& is_cell_empty(puzzle->cur_node, next->cell_idx))
		{
			*i_out = i;
			return (1);
		}
		i++;
	}
	*i_out = i;
	return (0);
}

int	get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_order	*cache;
	int				i;

	cache = &puzzle->cur_node->order_caches[get_cache_index(puzzle->cur_node)];
	rebuild_cache_if_stale(puzzle, cache, config);
	i = cache->lowest_valid_idx;
	while (i < cache->count)
	{
		if (is_cell_empty(puzzle->cur_node, cache->entries[i].cell_idx)
			&& is_valid_value(puzzle->cur_node, cache->entries[i].cell_idx,
				cache->entries[i].cell_val))
		{
			if (check_selective_filter(puzzle->cur_node,
				cache->entries[i].cell_idx, puzzle->size, config->is_selective))
			{
				*next = cache->entries[i];
				return (1);
			}
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
	rebuild_cache_if_stale(puzzle, cache, config);
	if (resume_next_from_cache(puzzle, next, cache, &i))
		return (1);
	while (i < cache->count)
	{
		if (is_cell_empty(puzzle->cur_node, cache->entries[i].cell_idx)
			&& check_selective_filter(puzzle->cur_node,
				cache->entries[i].cell_idx, puzzle->size, config->is_selective))
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
