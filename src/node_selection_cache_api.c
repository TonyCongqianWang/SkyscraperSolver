/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_api.c                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/19 19:35:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/19 19:35:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

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
		next->cell_idx = puzzle->cur_node->order_caches[sf]
			->entries[i].cell_idx;
		next->cell_val = 1;
		if (is_cell_empty(puzzle->cur_node, next->cell_idx)
			&& check_sel_filter(puzzle->cur_node, next->cell_idx,
				puzzle->size, config->is_selective)
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
