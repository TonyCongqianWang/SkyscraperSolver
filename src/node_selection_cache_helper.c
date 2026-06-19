/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_helper.c                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 11:03:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 16:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

static int	scan_and_check_entry(t_puzzle *puzzle, t_node_transition *next,
				t_node_order *cache, int *i_ptr)
{
	int	i;

	i = *i_ptr;
	while (i < cache->count && cache->entries[i].cell_idx != next->cell_idx)
		i++;
	if (i < cache->count)
	{
		next->cell_val++;
		if (set_next_valid_val(puzzle, next)
			&& is_cell_empty(puzzle->cur_node, next->cell_idx))
		{
			*i_ptr = i;
			return (1);
		}
		i++;
	}
	*i_ptr = i;
	return (0);
}

int	resume_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
		int sf_idx, int *i_out)
{
	t_node_order	*cache;
	int				lowest_empty;

	cache = puzzle->cur_node->order_caches[sf_idx];
	lowest_empty = 0;
	if (!puzzle->cur_node->is_in_lookahead_select)
		lowest_empty = puzzle->cur_node->lowest_empty_idx[sf_idx];
	if (next->cell_idx < 0)
	{
		*i_out = lowest_empty;
		return (0);
	}
	*i_out = lowest_empty;
	return (scan_and_check_entry(puzzle, next, cache, i_out));
}

int	try_cached_entry(t_puzzle *puzzle, t_node_transition *next,
		t_node_order *cache, int i)
{
	int	cell;
	int	cached_val;

	cell = cache->entries[i].cell_idx;
	cached_val = cache->entries[i].cell_val;
	if (is_valid_value(puzzle->cur_node, cell, cached_val))
	{
		*next = cache->entries[i];
		return (1);
	}
	next->cell_idx = cell;
	next->cell_val = 1;
	return (set_next_valid_val(puzzle, next)
		&& is_cell_empty(puzzle->cur_node, next->cell_idx));
}

void	collect_cache_entries(t_puzzle *puzzle, t_node_order *cache,
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
