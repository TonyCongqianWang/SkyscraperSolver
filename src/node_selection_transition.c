/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_utils.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 11:02:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 11:02:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_transition.h"

int	get_score_family_idx(t_score_family sf)
{
	return ((int)sf);
}

int	check_sel(t_node_state *node, int idx, t_node_select_config *conf)
{
	int	r;
	int	c;

	if (!node->is_in_lookahead_select || conf->selectivity == SELECTIVITY_NONE)
		return (1);
	r = idx / node->size;
	c = idx % node->size;
	if (conf->selectivity == SELECTIVITY_ANY_CHANGE)
	{
		return ((node->rows_changed_since_prune & (1 << r))
			|| (node->cols_changed_since_prune & (1 << c))
			|| (node->rows_invalid_since_prune & (1 << r))
			|| (node->cols_invalid_since_prune & (1 << c)));
	}
	else if (conf->selectivity == SELECTIVITY_VALUE_SET)
	{
		return ((node->rows_changed_since_prune & (1 << r))
			|| (node->cols_changed_since_prune & (1 << c)));
	}
	return (1);
}

void	init_node_transition(t_node_transition *tr)
{
	tr->cell_idx = -1;
	tr->cell_val = 1;
	tr->score = 0.0;
	tr->num_valids_col = 0;
	tr->num_valids_row = 0;
	tr->num_valids_cell = 0;
}

void	sync_cache_stacks(t_puzzle *puzzle)
{
	int				idx;
	t_node_order	*stack;

	if (puzzle->cur_node->order_cache)
	{
		stack = &puzzle->order_stack.orders[0];
		idx = puzzle->cur_node->order_cache - stack;
		puzzle->order_stack.top_idx = idx;
		while (++idx < MAX_STACK_DEPTH)
			puzzle->order_stack.orders[idx].build_depth = -1;
	}
}

int	check_sel_filter(t_node_state *node, int cell_idx,
		int size, t_selectivity_level selectivity)
{
	if (!node->is_in_lookahead_select || selectivity == SELECTIVITY_NONE)
		return (1);
	if (selectivity == SELECTIVITY_ANY_CHANGE)
	{
		return ((node->rows_changed_since_prune & (1 << (cell_idx / size)))
			|| (node->cols_changed_since_prune & (1 << (cell_idx % size)))
			|| (node->rows_invalid_since_prune & (1 << (cell_idx / size)))
			|| (node->cols_invalid_since_prune & (1 << (cell_idx % size))));
	}
	else if (selectivity == SELECTIVITY_VALUE_SET)
	{
		return ((node->rows_changed_since_prune & (1 << (cell_idx / size)))
			|| (node->cols_changed_since_prune & (1 << (cell_idx % size))));
	}
	return (1);
}
