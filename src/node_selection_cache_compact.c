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

static void	copy_valid_back(t_node_order *cache, t_node_transition *tmp_entries,
				t_transition_meta *tmp_meta, int valid_count)
{
	int	i;

	i = 0;
	while (i < valid_count)
	{
		cache->entries[i] = tmp_entries[i];
		cache->meta[i] = tmp_meta[i];
		i++;
	}
	cache->count = valid_count;
	cache->num_valid = valid_count;
}

void	compact_and_sort_cache(t_node_state *node, t_node_order *cache,
			t_selection_criterion criterion)
{
	t_node_transition	tmp_entries[MAX_TRANSITIONS];
	t_transition_meta	tmp_meta[MAX_TRANSITIONS];
	int					i;
	int					valid_count;

	valid_count = 0;
	i = 0;
	while (i < cache->count)
	{
		if (is_cell_empty(node, cache->entries[i].cell_idx)
			&& is_valid_value(node, cache->entries[i].cell_idx,
				cache->entries[i].cell_val))
		{
			tmp_entries[valid_count] = cache->entries[i];
			tmp_meta[valid_count] = cache->meta[i];
			valid_count++;
		}
		i++;
	}
	copy_valid_back(cache, tmp_entries, tmp_meta, valid_count);
	sort_node_order_meta(cache->entries, cache->meta, cache->count, criterion);
}
