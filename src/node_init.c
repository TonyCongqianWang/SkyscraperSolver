/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_init.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/20 18:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/20 18:20:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_init.h"
#include "cell_bounds.h"
#include <stddef.h>

static void	init_node_grid(t_node_state *node, int size);
static void	init_root_search_state(t_node_state *node, int size);
static void	init_root_pruning_state(t_node_state *node, int size);
static void	init_root_selection_state(t_node_state *node);

void	init_root_node(t_node_state *root_node, int size)
{
	init_root_search_state(root_node, size);
	init_root_pruning_state(root_node, size);
	init_root_selection_state(root_node);
	init_node_grid(root_node, size);
}

static void	init_root_search_state(t_node_state *node, int size)
{
	node->size = size;
	node->is_complete = 0;
	node->is_invalid = 0;
	node->sub_node_depth = 0;
	node->cur_depth = 0;
	node->last_set_idx = -1;
	node->max_depth = size * size;
	node->num_unset = size * size;
	node->target_nunset = 0;
	node->remaining_entropy = 0;
	node->last_entropy[0] = 0;
	node->last_entropy[1] = 0;
	node->last_entropy[2] = 0;
	node->last_entropy[3] = 0;
	node->solutions_found = 0;
	node->max_solutions = node->puzzle->max_solutions;
}

static void	init_root_pruning_state(t_node_state *node, int size)
{
	node->last_prune_nunset = size * size + 1;
	node->rows_changed_since_prune = 0xffff;
	node->cols_changed_since_prune = 0xffff;
	node->rows_invalid_since_prune = 0xffff;
	node->cols_invalid_since_prune = 0xffff;
	node->dirty_constrs.count = 0;
	node->dirty_constrs.in_stack_bmp = 0;
}

static void	init_root_selection_state(t_node_state *node)
{
	node->is_in_lookahead_select = 0;
	node->is_in_neg_lookahead = 0;
	node->lookahead_selectivity = SELECTIVITY_NONE;
	node->lookahead_ctx = NULL;
	node->order_cache = &node->puzzle->order_stack.orders[0];
	node->lowest_empty_idx = 0;
}

static void	init_node_grid(t_node_state *node, int size)
{
	int		idx;
	int		v;

	idx = 0;
	while (idx < size * size)
	{
		node->grid.vals[idx] = 0;
		node->grid.valid_val_bmps[idx] = 0xffff;
		update_cell_bounds(node, idx);
		node->grid.num_cell_vals[idx] = size;
		v = 0;
		while (v < MAX_SIZE + 1)
		{
			node->lookahead_scores[idx][v] = 0.0;
			v++;
		}
		idx++;
	}
}
