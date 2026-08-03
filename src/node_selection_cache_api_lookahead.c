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

static int	scan_lookahead_pass(t_puzzle *puzzle, t_node_transition *next,
				int pass)
{
	t_node_state		*node;
	int					cell_idx;
	t_node_transition	entry;

	node = puzzle->cur_node;
	while (node->lookahead_ctx->curr_index < node->order_cache->count)
	{
		entry = node->order_cache->entries[node->lookahead_ctx->curr_index];
		cell_idx = entry.cell_idx;
		if (is_cell_empty(node, cell_idx)
			&& node->lookahead_ctx->cell_passes[cell_idx] == pass)
		{
			if (is_valid_value(node, cell_idx, entry.cell_val))
			{
				*next = entry;
				return (1);
			}
		}
		node->lookahead_ctx->curr_index++;
	}
	(void)puzzle;
	return (0);
}

static int	find_resume_index(t_node_order *cache, t_node_transition *next)
{
	int	i;

	i = 0;
	while (i < cache->count)
	{
		if (cache->entries[i].cell_idx == next->cell_idx
			&& cache->entries[i].cell_val == next->cell_val)
			return (i);
		i++;
	}
	return (-1);
}

static void	update_resume_index(t_node_state *node, t_node_transition *next)
{
	int	i;

	i = node->lookahead_ctx->curr_index;
	if (i >= 0 && i < node->order_cache->count
		&& node->order_cache->entries[i].cell_idx == next->cell_idx
		&& node->order_cache->entries[i].cell_val == next->cell_val)
		node->lookahead_ctx->curr_index = i + 1;
	else
		node->lookahead_ctx->curr_index
			= find_resume_index(node->order_cache, next) + 1;
}

int	get_next_lookahead(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_state	*node;
	int				max_pass;

	node = puzzle->cur_node;
	if (next->cell_idx >= 0)
		update_resume_index(node, next);
	else
		node->lookahead_ctx->curr_index = 0;
	max_pass = get_max_allowed_pass(config->selectivity);
	while (node->lookahead_ctx->curr_pass <= max_pass)
	{
		if (scan_lookahead_pass(puzzle, next, node->lookahead_ctx->curr_pass))
			return (1);
		node->lookahead_ctx->curr_pass++;
		node->lookahead_ctx->curr_index = 0;
	}
	return (0);
}
