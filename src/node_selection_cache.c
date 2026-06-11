#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"
#include <stdio.h>
#include <stdlib.h>

static t_node_order	*get_cache_for_rebuild(t_puzzle *puzzle, int sf)
{
	t_node_state	*node;
	t_node_order	*current_cache;

	node = puzzle->cur_node;
	current_cache = node->order_caches[sf];
	if (!current_cache || current_cache->build_depth < node->cur_depth)
	{
		puzzle->order_stacks.stacks[sf].top_idx++;
		if (puzzle->order_stacks.stacks[sf].top_idx >= MAX_STACK_DEPTH)
		{
			fprintf(stderr, "Fatal error: Cache stack overflow for family %d\n", sf);
			exit(1);
		}
		node->order_caches[sf] = &puzzle->order_stacks.stacks[sf].orders[puzzle->order_stacks.stacks[sf].top_idx];
	}
	return (node->order_caches[sf]);
}

void	build_node_order(t_puzzle *puzzle, t_node_select_config *config)
{
	t_node_state		*node;
	t_node_order		*cache;
	int					cell_idx;
	t_node_transition	best;
	int					sf;

	node = puzzle->cur_node;
	sf = config->score_family;
	cache = get_cache_for_rebuild(puzzle, sf);
	cache->count = 0;
	node->lowest_valid_idx[0] = 0;
	node->lowest_valid_idx[1] = 0;
	node->lowest_valid_idx[2] = 0;
	cache->build_depth = node->cur_depth;
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

void	rebuild_cache_if_stale(t_puzzle *puzzle,
			t_node_select_config *config)
{
	t_node_state	*node;
	t_node_order	*cache;
	int				sf;

	node = puzzle->cur_node;
	sf = config->score_family;
	cache = node->order_caches[sf];
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
	int				sf;
	int				ci;

	sf = config->score_family;
	ci = get_consumer_index(puzzle->cur_node);
	cache = puzzle->cur_node->order_caches[sf];
	i = puzzle->cur_node->lowest_valid_idx[ci];
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
		if (i == puzzle->cur_node->lowest_valid_idx[ci])
			puzzle->cur_node->lowest_valid_idx[ci]++;
		i++;
	}
	return (0);
}

int	get_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_order	*cache;
	int				i;
	int				sf;
	int				ci;

	sf = config->score_family;
	ci = get_consumer_index(puzzle->cur_node);
	cache = puzzle->cur_node->order_caches[sf];
	if (resume_next_from_cache(puzzle, next, cache, &puzzle->cur_node->lowest_valid_idx[ci], &i))
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
		if (i == puzzle->cur_node->lowest_valid_idx[ci])
			puzzle->cur_node->lowest_valid_idx[ci]++;
		i++;
	}
	return (0);
}

void	sync_cache_stacks(t_puzzle *puzzle)
{
	t_node_state	*node;
	int				sf;
	int				idx;

	node = puzzle->cur_node;
	sf = 0;
	while (sf < 3)
	{
		if (node->order_caches[sf])
		{
			idx = node->order_caches[sf] - &puzzle->order_stacks.stacks[sf].orders[0];
			puzzle->order_stacks.stacks[sf].top_idx = idx;
		}
		sf++;
	}
}
