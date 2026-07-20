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

static void	init_node_grid(t_node_state *node, int size);
static void	init_node_order_ptrs(t_node_state *node);

void	init_root_node(t_node_state *root_node, int size)
{
	root_node->size = size;
	root_node->is_complete = 0;
	root_node->is_invalid = 0;
	root_node->sub_node_depth = 0;
	root_node->cur_depth = 0;
	root_node->last_set_idx = -1;
	root_node->max_depth = size * size;
	root_node->num_unset = size * size;
	root_node->target_nunset = 0;
	root_node->last_prune_nunset = size * size + 1;
	root_node->rows_changed_since_prune = 0xffff;
	root_node->cols_changed_since_prune = 0xffff;
	root_node->rows_invalid_since_prune = 0xffff;
	root_node->cols_invalid_since_prune = 0xffff;
	root_node->is_in_lookahead_select = 0;
	init_node_order_ptrs(root_node);
	root_node->remaining_entropy = 0;
	root_node->last_entropy[0] = 0;
	root_node->last_entropy[1] = 0;
	root_node->last_entropy[2] = 0;
	root_node->last_entropy[3] = 0;
	root_node->solutions_found = 0;
	root_node->max_solutions = root_node->puzzle->max_solutions;
	init_node_grid(root_node, size);
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

static void	init_node_order_ptrs(t_node_state *node)
{
	node->order_cache = &node->puzzle->order_stack.orders[0];
	node->lowest_empty_idx = 0;
}
