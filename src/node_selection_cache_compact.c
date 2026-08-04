/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_compact.c                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_eval.h"
#include "grid_availability.h"
#include "node_selection_score.h"

void	sort_node_order_meta(t_node_transition *entries,
			t_transition_meta *meta, int count,
			t_selection_criterion criterion)
{
	int					i;
	int					j;
	t_node_transition	key_entry;
	t_transition_meta	key_meta;

	i = 1;
	while (i < count)
	{
		key_entry = entries[i];
		key_meta = meta[i];
		j = i - 1;
		while (j >= 0 && ((criterion == SELECT_MAX
					&& entries[j].score < key_entry.score)
				|| (criterion == SELECT_MIN
					&& entries[j].score > key_entry.score)))
		{
			entries[j + 1] = entries[j];
			meta[j + 1] = meta[j];
			j--;
		}
		entries[j + 1] = key_entry;
		meta[j + 1] = key_meta;
		i++;
	}
}

void	compact_and_sort_cache(t_node_state *node, t_node_order *cache,
			t_selection_criterion criterion)
{
	int	read_idx;
	int	write_idx;

	write_idx = 0;
	read_idx = 0;
	while (read_idx < cache->count)
	{
		if (is_cell_empty(node, cache->entries[read_idx].cell_idx)
			&& is_valid_value(node, cache->entries[read_idx].cell_idx,
				cache->entries[read_idx].cell_val))
		{
			if (write_idx != read_idx)
			{
				cache->entries[write_idx] = cache->entries[read_idx];
				cache->meta[write_idx] = cache->meta[read_idx];
			}
			write_idx++;
		}
		read_idx++;
	}
	cache->count = write_idx;
	cache->num_valid = write_idx;
	recalculate_cache_scores(node, cache);
	sort_node_order_meta(cache->entries, cache->meta, cache->count, criterion);
}
