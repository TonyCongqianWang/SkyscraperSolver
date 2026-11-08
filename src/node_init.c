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
static void	init_root_pruning_state(t_node_state *node);
static void	init_root_selection_state(t_node_state *node);

void	init_root_node(t_node_state *root_node, int size)
{
	init_root_search_state(root_node, size);
	init_root_pruning_state(root_node);
	init_root_selection_state(root_node);
	init_node_grid(root_node, size);
}

static void	init_root_search_state(t_node_state *node, int size)
{
	node->size = size;
	node->domain.is_complete = 0;
	node->domain.is_invalid = 0;
	node->tree.lookahead_depth = 0;
	node->tree.neg_lookahead_depth = 0;
	node->tree.depth = 0;
	node->last_set_idx = -1;
	node->search_policy.limits.max_depth = size * size;
	node->domain.num_unset = size * size;
	node->search_policy.limits.target_nunset = 0;
	node->domain.remaining_entropy = 0;
	node->last_entropy[0] = 0;
	node->last_entropy[1] = 0;
	node->last_entropy[2] = 0;
	node->search_policy.limits.max_solutions = node->solver->max_solutions;
}

static void	init_root_pruning_state(t_node_state *node)
{
	node->rows_changed_since_prune = 0xffff;
	node->cols_changed_since_prune = 0xffff;
	node->rows_invalid_since_prune = 0xffff;
	node->cols_invalid_since_prune = 0xffff;
	node->dirty_constrs.count = 0;
	node->dirty_constrs.in_stack_bmp = 0;
}

static void	init_root_selection_state(t_node_state *node)
{
	node->search_policy.branch.is_in_lookahead_select = 0;
	node->search_policy.branch.lookahead_selectivity = SELECTIVITY_NONE;
	node->lookahead_ctx = NULL;
	node->order_cache = &node->solver->order_stack.orders[0];
}

static void	init_node_grid(t_node_state *node, int size)
{
	int		idx;

	idx = 0;
	while (idx < size * size)
	{
		node->domain.vals[idx] = 0;
		node->domain.valid_val_bmps[idx] = 0xffff;
		update_cell_bounds(node, idx);
		node->domain.num_cell_vals[idx] = size;
		idx++;
	}
}
