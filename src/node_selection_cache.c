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
	int					sf_idx;

	node = puzzle->cur_node;
	sf_idx = get_score_family_idx(config->score_family);
	cache = get_cache_for_rebuild(puzzle, sf_idx);
	cache->count = 0;
	node->lowest_valid_idx[sf_idx] = 0;
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
	int				cached_val;

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
			cached_val = cache->entries[i].cell_val;
			if (is_valid_value(puzzle->cur_node, cell, cached_val))
			{
				*next = cache->entries[i];
				return (1);
			}
			next->cell_idx = cell;
			next->cell_val = 1;
			if (set_next_valid_val(puzzle, next)
				&& is_cell_empty(puzzle->cur_node, next->cell_idx))
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
	int				*lowest_valid_idx_ptr;
	int				dummy_lowest_valid_idx;
	int				cell;

	sf_idx = get_score_family_idx(config->score_family);
	cache = puzzle->cur_node->order_caches[sf_idx];
	if (puzzle->cur_node->is_in_lookahead_select)
	{
		dummy_lowest_valid_idx = 0;
		lowest_valid_idx_ptr = &dummy_lowest_valid_idx;
	}
	else
		lowest_valid_idx_ptr = &puzzle->cur_node->lowest_valid_idx[sf_idx];
	if (resume_next_from_cache(puzzle, next, cache, lowest_valid_idx_ptr, &i))
		return (1);
	while (i < cache->count)
	{
		cell = cache->entries[i].cell_idx;
		if (is_cell_empty(puzzle->cur_node, cell)
			&& check_sel_filter(puzzle->cur_node, cell, puzzle->size,
				config->is_selective))
		{
			next->cell_idx = cell;
			next->cell_val = 1;
			if (set_next_valid_val(puzzle, next)
				&& is_cell_empty(puzzle->cur_node, next->cell_idx))
				return (1);
		}
		if (i == *lowest_valid_idx_ptr)
			(*lowest_valid_idx_ptr)++;
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
