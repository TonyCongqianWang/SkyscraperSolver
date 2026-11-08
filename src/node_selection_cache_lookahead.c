/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_lookahead.c                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/06 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/06 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"

void	node_order_record_probe(t_node_order *cache, t_node_transition next,
			t_lookahead_pass pass, int entropy)
{
	int	i;

	if (!cache)
		return ;
	i = 0;
	while (i < cache->count)
	{
		if (cache->entries[i].cell_idx == next.cell_idx
			&& cache->entries[i].cell_val == next.cell_val)
		{
			if (pass == LOOKAHEAD_NEG)
				cache->meta[i].entropy_neg = entropy;
			else
				cache->meta[i].entropy_pos = entropy;
			break ;
		}
		i++;
	}
}

void	node_order_finish_lookahead(t_node_state *node,
			t_lookahead_pass passes)
{
	if (node->tree.lookahead_depth != 0 || passes != LOOKAHEAD_BOTH)
		return ;
	node->order_cache->lookahead_build_entropy = node->domain.remaining_entropy;
	node->order_cache->needs_rebuild = 1;
}
