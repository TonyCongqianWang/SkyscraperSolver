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
	cache->meta[cache->count].entropy_pos = -1;
	cache->meta[cache->count].entropy_neg = -1;
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

void	init_order_stacks(t_puzzle *puzzle)
{
	int				stack_idx;
	t_node_order	*order;

	puzzle->order_stack.top_idx = 0;
	stack_idx = 0;
	while (stack_idx < MAX_STACK_DEPTH)
	{
		order = &puzzle->order_stack.orders[stack_idx];
		order->last_build_entropy = -1;
		order->build_depth = -1;
		stack_idx++;
	}
}

void	rebuild_cache_if_stale(t_puzzle *puzzle,
			t_node_select_config *config, int allow_stale_rebuild)
{
	t_node_state	*node;
	t_node_order	*cache;
	int				is_stale;

	node = puzzle->cur_node;
	cache = node->order_cache;
	if (cache->last_build_entropy == -1)
		is_stale = 1;
	else if (!allow_stale_rebuild)
		is_stale = 0;
	else
		is_stale = (cache->last_build_entropy - node->remaining_entropy
				> config->rebuild_period);
	if (is_stale)
		build_node_order(puzzle, config);
}
