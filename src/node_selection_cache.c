/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
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

static int	handle_resume_cell(t_puzzle *puzzle, t_node_transition *next,
				t_node_select_config *config)
{
	next->cell_val = config->start_cell_val;
	config->start_cell_idx = -1;
	config->start_cell_val = 1;
	if (!set_next_valid_val(puzzle, next))
	{
		if (puzzle->cur_node->is_in_lookahead_select)
			return (2);
		return (0);
	}
	return (1);
}

static int	process_cache_entry(t_puzzle *puzzle, t_node_transition *next,
				t_node_select_config *config, t_node_transition *entry)
{
	if (config->start_cell_idx < 0 && !is_valid_value(puzzle->cur_node,
			entry->cell_idx, entry->cell_val))
	{
		set_best_val_strat(puzzle, entry->cell_idx, entry, config);
		if (entry->cell_idx == -1)
			return (0);
	}
	*next = *entry;
	if (config->start_cell_idx < 0)
		return (1);
	return (handle_resume_cell(puzzle, next, config));
}

static int	scan_cache_from(t_puzzle *puzzle, t_node_transition *next,
				t_node_select_config *config)
{
	t_node_order	*cache;
	int				i;
	int				res;

	cache = &puzzle->cur_node->order_caches[get_cache_index(puzzle->cur_node)];
	i = 0;
	while (config->start_cell_idx >= 0 && i < cache->count
		&& cache->entries[i].cell_idx != config->start_cell_idx)
		i++;
	while (i < cache->count)
	{
		if (is_cell_empty(puzzle->cur_node, cache->entries[i].cell_idx)
			&& (!config->is_selective
				|| (puzzle->cur_node->rows_changed_since_prune
					& (1 << (cache->entries[i].cell_idx / puzzle->size)))
				|| (puzzle->cur_node->cols_changed_since_prune
					& (1 << (cache->entries[i].cell_idx % puzzle->size)))))
		{
			res = process_cache_entry(puzzle, next, config, &cache->entries[i]);
			if (res != 2)
				return (res);
		}
		i++;
	}
	return (0);
}

int	get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_state	*node;
	t_node_order	*cache;

	node = puzzle->cur_node;
	cache = &node->order_caches[get_cache_index(node)];
	if (!node->is_in_lookahead_select && node->progress_counter
		>= cache->last_build_prog + config->rebuild_period)
		build_node_order(puzzle, config);
	return (scan_cache_from(puzzle, next, config));
}
