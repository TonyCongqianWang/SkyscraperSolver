/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_api_lookahead.c               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/24 22:50:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/24 22:50:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

static int	check_lookahead_candidate(t_puzzle *puzzle, t_node_transition *next,
				int cell_idx)
{
	next->cell_idx = cell_idx;
	next->cell_val = 1;
	return (set_next_valid_val(puzzle, next)
		&& is_cell_empty(puzzle->cur_node, cell_idx));
}

static int	scan_lookahead_pass(t_puzzle *puzzle, t_node_transition *next,
				int pass)
{
	t_node_state	*node;
	int				cell_idx;

	node = puzzle->cur_node;
	while (node->lookahead_ctx->curr_index < node->order_cache->count)
	{
		cell_idx = node->order_cache->entries[
			node->lookahead_ctx->curr_index].cell_idx;
		if (is_cell_empty(node, cell_idx)
			&& node->lookahead_ctx->cell_passes[cell_idx] == pass)
		{
			if (check_lookahead_candidate(puzzle, next, cell_idx))
				return (1);
		}
		node->lookahead_ctx->curr_index++;
	}
	return (0);
}

int	get_next_lookahead(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_state	*node;
	int				max_pass;

	node = puzzle->cur_node;
	if (next->cell_idx >= 0)
	{
		next->cell_val++;
		if (set_next_valid_val(puzzle, next)
			&& is_cell_empty(node, next->cell_idx))
			return (1);
		node->lookahead_ctx->curr_index++;
	}
	max_pass = get_max_allowed_pass(config->selectivity);
	while (node->lookahead_ctx->curr_pass <= max_pass)
	{
		if (scan_lookahead_pass(puzzle, next, node->lookahead_ctx->curr_pass))
			return (1);
		node->lookahead_ctx->curr_pass++;
		node->lookahead_ctx->curr_index = node->lowest_empty_idx;
	}
	return (0);
}
