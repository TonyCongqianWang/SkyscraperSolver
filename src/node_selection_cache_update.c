/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_helper.c                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 11:03:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 18:50:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"
#include "node_selection_score.h"
#include "node_selection_transition.h"

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

static int	find_transition_in_cache(t_node_order *cache, int cell, int val)
{
	int	i;

	if (!cache)
		return (-1);
	i = 0;
	while (i < cache->count)
	{
		if (cache->entries[i].cell_idx == cell
			&& cache->entries[i].cell_val == val)
			return (i);
		i++;
	}
	return (-1);
}

static void	copy_parent_entropy(t_puzzle *puzzle, t_node_order *cache,
				int c, int v)
{
	int	parent_top;
	int	old_idx;
	int	write_idx;

	parent_top = puzzle->order_stack.top_idx - 1;
	old_idx = -1;
	if (parent_top >= 0)
		old_idx = find_transition_in_cache(
				&puzzle->order_stack.orders[parent_top], c, v);
	write_idx = cache->count;
	cache->meta[write_idx].entropy_pos = -1;
	cache->meta[write_idx].entropy_neg = -1;
	if (old_idx >= 0)
	{
		cache->meta[write_idx].entropy_pos = puzzle->order_stack
			.orders[parent_top].meta[old_idx].entropy_pos;
		cache->meta[write_idx].entropy_neg = puzzle->order_stack
			.orders[parent_top].meta[old_idx].entropy_neg;
	}
}

static void	add_transition(t_puzzle *puzzle, t_node_order *cache,
				t_node_select_config *config, int cv)
{
	t_node_transition	tr;
	int					c;
	int					v;

	init_node_transition(&tr);
	c = cv >> 8;
	v = cv & 0xFF;
	tr.cell_idx = c;
	tr.cell_val = v;
	score_transition_strat(puzzle->cur_node, &tr, config->score_family);
	cache->entries[cache->count] = tr;
	cache->meta[cache->count].cached_br_score = tr.score;
	copy_parent_entropy(puzzle, cache, c, v);
	cache->count++;
}

void	collect_cache_entries(t_puzzle *puzzle, t_node_order *cache,
			t_node_select_config *config)
{
	int				i;
	int				c;
	int				v;
	t_node_state	*state;

	state = puzzle->cur_node;
	cache->count = 0;
	i = 0;
	while (i < puzzle->squared_size)
	{
		c = puzzle->cell_distance_order[i];
		if (is_cell_empty(state, c))
		{
			v = puzzle->size;
			while (v >= 1)
			{
				if (is_valid_value(state, c, v))
					add_transition(puzzle, cache, config, (c << 8) | v);
				v--;
			}
		}
		i++;
	}
}
