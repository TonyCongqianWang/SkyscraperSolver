/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   line_order.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:40:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:40:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "line_order.h"

t_line_order	*get_line_order(t_node_state *node)
{
	t_puzzle	*puzzle;
	int			idx;

	puzzle = node->puzzle;
	idx = node->order_cache - puzzle->order_stack.orders;
	return (&puzzle->line_order_stack.orders[idx]);
}

void	init_line_order_stack(t_puzzle *puzzle)
{
	t_line_order	*order;
	int				i;

	order = &puzzle->line_order_stack.orders[0];
	order->count = 2 * puzzle->size;
	i = 0;
	while (i < order->count)
	{
		order->entries[i].constr_idx = i;
		i++;
	}
	sort_line_order(puzzle->cur_node);
}

void	copy_line_order(t_puzzle *puzzle, int parent_idx)
{
	puzzle->line_order_stack.orders[puzzle->order_stack.top_idx]
		= puzzle->line_order_stack.orders[parent_idx];
}
