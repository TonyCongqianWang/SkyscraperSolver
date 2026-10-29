/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   line_order_sort.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:40:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:40:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "line_order.h"
#include "entropy.h"

static void	update_line_scores(t_node_state *node, t_line_order *order)
{
	int	i;
	int	idx;

	i = 0;
	while (i < order->count)
	{
		idx = order->entries[i].constr_idx;
		order->entries[i].entropy = compute_constr_entropy(node, idx,
				node->size);
		i++;
	}
}

void	sort_line_order(t_node_state *node)
{
	t_line_order	*order;
	t_line_priority	entry;
	int				i;
	int				j;

	order = get_line_order(node);
	update_line_scores(node, order);
	i = 1;
	while (i < order->count)
	{
		entry = order->entries[i];
		j = i;
		while (j > 0 && order->entries[j - 1].entropy > entry.entropy)
		{
			order->entries[j] = order->entries[j - 1];
			j--;
		}
		order->entries[j] = entry;
		i++;
	}
}
