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

#include "work_instrumentation.h"
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
		work_micro_begin(WORK_LINE_SCORE);
		work_add(WORK_LINE_SCORE, 1);
		work_add(WORK_LINE_SCORE_VALUE, node->size);
		order->entries[i].entropy = compute_constr_entropy(node, idx,
				node->size);
		work_micro_end(WORK_LINE_SCORE);
		i++;
	}
}

static int	line_needs_shift(t_line_priority *left, t_line_priority *right)
{
	int	result;

	work_micro_begin(WORK_LINE_COMPARE);
	result = left->entropy > right->entropy;
	work_micro_end(WORK_LINE_COMPARE);
	return (result);
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
		while (j > 0 && line_needs_shift(&order->entries[j - 1], &entry))
		{
			work_sort_shift(WORK_LINE_COMPARE, WORK_LINE_SHIFT);
			work_micro_begin(WORK_LINE_SHIFT);
			order->entries[j] = order->entries[j - 1];
			work_micro_end(WORK_LINE_SHIFT);
			j--;
		}
		work_add(WORK_LINE_COMPARE, j > 0);
		order->entries[j] = entry;
		i++;
	}
}
