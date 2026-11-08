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

void	init_node_transition(t_node_transition *tr)
{
	tr->cell_idx = -1;
	tr->cell_val = 1;
	tr->score = 0.0;
	tr->num_valids_col = 0;
	tr->num_valids_row = 0;
	tr->num_valids_cell = 0;
}

void	sync_cache_stacks(t_solver_state *puzzle)
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
