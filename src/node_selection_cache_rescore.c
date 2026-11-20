/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_rescore.c                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_score.h"
#include "transition_scoring.h"
#include "grid_availability.h"

void	rescore_cache_entries(t_node_state *node, t_node_order *cache)
{
	t_node_transition	entry;
	int					i;

	i = -1;
	while (++i < cache->items.count)
	{
		entry = cache->items.entries[i];
		if (is_cell_empty(node, entry.cell_idx)
			&& is_valid_value(node, entry.cell_idx, entry.cell_val))
		{
			score_transition_strat(node, &entry);
			cache->items.meta[i].cached_br_score = entry.score;
			entry.score = cache->items.entries[i].score;
			cache->items.entries[i] = entry;
		}
	}
	cache->state.scores_dirty = 1;
}
