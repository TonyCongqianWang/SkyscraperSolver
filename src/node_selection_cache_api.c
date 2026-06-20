/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_api.c                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/19 19:35:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 01:25:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

#ifndef USE_CONSTRS_SCORING
# define USE_CONSTRS_SCORING 0
#endif

void	rebuild_cache_if_stale(t_puzzle *puzzle,
			t_node_select_config *config, int allow_stale_rebuild)
{
	t_node_state	*node;
	t_node_order	*cache;
	int				is_stale;

	node = puzzle->cur_node;
	cache = node->order_cache;
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

static double	get_best_possible_score(t_node_state *state,
					t_node_select_config *config)
{
	int	size;

	size = state->size;
	if (config->score_family == SCORE_BRANCHING)
	{
		if (USE_CONSTRS_SCORING)
			return ((double)((size + 1) * (size + 1) - (size + 1) - 1));
		else
			return ((double)((size + 1) * (size + 1) * (size + 1) * (size + 1)
				- (size + 1) * (size + 1) * (size + 1) - (size + 1)));
	}
	else if (config->score_family == SCORE_MIN_CANDIDATES)
		return (1.0);
	return (-1e9);
}

static int	check_and_rescore_best(t_puzzle *puzzle, t_node_transition *next,
				t_node_transition *best, t_node_select_config *config,
				int i, double best_possible)
{
	t_node_order		*cache;
	t_node_transition	candidate;
	double				cached_score;

	cache = puzzle->cur_node->order_cache;
	cached_score = cache->entries[i].score;
	if ((config->criterion == SELECT_MAX && cached_score >= best_possible)
		|| (config->criterion == SELECT_MIN && cached_score <= best_possible))
	{
		if (try_cached_entry(puzzle, next, cache, i))
			return (1);
	}
	set_best_val_strat(puzzle, cache->entries[i].cell_idx, &candidate, config);
	if (candidate.cell_idx != -1)
	{
		if ((config->criterion == SELECT_MAX && candidate.score >= best_possible)
			|| (config->criterion == SELECT_MIN && candidate.score <= best_possible))
		{
			*next = candidate;
			return (1);
		}
		if (best->cell_idx == -1
			|| (config->criterion == SELECT_MAX && candidate.score > best->score)
			|| (config->criterion == SELECT_MIN && candidate.score < best->score))
			*best = candidate;
	}
	return (0);
}

int	get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_order		*cache;
	t_node_state		*node;
	t_node_transition	best;
	double				best_possible;
	int					i;

	node = puzzle->cur_node;
	cache = node->order_cache;
	best_possible = get_best_possible_score(node, config);
	best.cell_idx = -1;
	i = node->lowest_empty_idx;
	while (i < cache->count)
	{
		if (is_cell_empty(node, cache->entries[i].cell_idx)
			&& check_sel_filter(node, cache->entries[i].cell_idx,
				puzzle->size, config->selectivity))
		{
			if (check_and_rescore_best(puzzle, next, &best, config, i, best_possible))
				return (1);
		}
		i++;
	}
	if (best.cell_idx != -1)
	{
		*next = best;
		return (1);
	}
	return (0);
}

static int	get_cell_priority_pass(t_node_state *node, int cell_idx, int size)
{
	int	r;
	int	c;

	r = cell_idx / size;
	c = cell_idx % size;
	if ((node->rows_changed_since_prune & (1 << r))
		|| (node->cols_changed_since_prune & (1 << c)))
		return (1);
	if ((node->rows_invalid_since_prune & (1 << r))
		|| (node->cols_invalid_since_prune & (1 << c)))
		return (2);
	return (3);
}

static int	get_max_allowed_pass(t_selectivity_level selectivity)
{
	if (selectivity == SELECTIVITY_VALUE_SET)
		return (1);
	if (selectivity == SELECTIVITY_ANY_CHANGE)
		return (2);
	return (3);
}

static int	get_next_in_pass(t_puzzle *puzzle, t_node_transition *next,
				t_node_order *cache, int *i, int pass)
{
	t_node_state	*node;
	int				cell_idx;

	node = puzzle->cur_node;
	while (*i < cache->count)
	{
		cell_idx = cache->entries[*i].cell_idx;
		if (is_cell_empty(node, cell_idx)
			&& get_cell_priority_pass(node, cell_idx, puzzle->size) == pass)
		{
			next->cell_idx = cell_idx;
			next->cell_val = 1;
			if (set_next_valid_val(puzzle, next)
				&& is_cell_empty(node, cell_idx))
				return (1);
		}
		(*i)++;
	}
	return (0);
}

static void	get_resume_pos(t_node_state *node, t_node_transition *next,
				t_node_order *cache, int *pass_out, int *i_out)
{
	int	i;

	if (next->cell_idx >= 0)
	{
		*pass_out = get_cell_priority_pass(node, next->cell_idx, node->size);
		i = 0;
		while (i < cache->count && cache->entries[i].cell_idx != next->cell_idx)
			i++;
		*i_out = i + 1;
	}
	else
	{
		*pass_out = 1;
		*i_out = 0;
	}
}

int	get_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_order	*cache;
	int				curr_pass;
	int				max_pass;
	int				i;

	cache = puzzle->cur_node->order_cache;
	if (next->cell_idx >= 0)
	{
		next->cell_val++;
		if (set_next_valid_val(puzzle, next)
			&& is_cell_empty(puzzle->cur_node, next->cell_idx))
			return (1);
	}
	get_resume_pos(puzzle->cur_node, next, cache, &curr_pass, &i);
	max_pass = get_max_allowed_pass(config->selectivity);
	while (curr_pass <= max_pass)
	{
		if (get_next_in_pass(puzzle, next, cache, &i, curr_pass))
			return (1);
		curr_pass++;
		i = 0;
	}
	return (0);
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
		order->last_build_prog = 0;
		order->build_depth = -1;
		stack_idx++;
	}
}
