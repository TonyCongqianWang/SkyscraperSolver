/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_api_next.c                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/21 18:52:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/24 22:50:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

int	get_cell_priority_pass(t_node_state *node, int cell_idx, int size)
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

int	get_max_allowed_pass(t_selectivity_level selectivity)
{
	if (selectivity == SELECTIVITY_VALUE_SET)
		return (1);
	if (selectivity == SELECTIVITY_ANY_CHANGE)
		return (2);
	return (3);
}

static int	get_next_in_pass(t_puzzle *puzzle, t_node_transition *next,
				int *i, int pass)
{
	t_node_state	*node;
	t_node_order	*cache;
	int				cell_idx;

	node = puzzle->cur_node;
	cache = node->order_cache;
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
				int *pass_out, int *i_out)
{
	t_node_order	*cache;
	int				i;

	cache = node->order_cache;
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
	t_node_state	*node;
	int				max_pass;
	int				curr_pass;
	int				i;

	node = puzzle->cur_node;
	if (node->lookahead_ctx)
		return (get_next_lookahead(puzzle, next, config));
	if (next->cell_idx >= 0)
	{
		next->cell_val++;
		if (set_next_valid_val(puzzle, next)
			&& is_cell_empty(node, next->cell_idx))
			return (1);
	}
	get_resume_pos(node, next, &curr_pass, &i);
	max_pass = get_max_allowed_pass(config->selectivity);
	while (curr_pass <= max_pass)
	{
		if (get_next_in_pass(puzzle, next, &i, curr_pass))
			return (1);
		curr_pass++;
		i = 0;
	}
	return (0);
}
