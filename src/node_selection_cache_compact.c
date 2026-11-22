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

#include "work_instrumentation.h"
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

	i = 0;
	while (++i < count)
	{
		key_entry = entries[i];
		key_meta = meta[i];
		j = i - 1;
		while (j >= 0 && ((criterion == SELECT_MAX
					&& entries[j].score < key_entry.score)
				|| (criterion == SELECT_MIN
					&& entries[j].score > key_entry.score)))
		{
			work_sort_shift(WORK_TRANSITION_COMPARE, WORK_TRANSITION_SHIFT);
			entries[j + 1] = entries[j];
			meta[j + 1] = meta[j];
			j--;
		}
		work_add(WORK_TRANSITION_COMPARE, j >= 0);
		entries[j + 1] = key_entry;
		meta[j + 1] = key_meta;
	}
}

static int	cache_entry_valid(t_node_state *node, t_order_items *items,
			int idx)
{
	int	keep;

	work_micro_begin(WORK_COMPACT_CHECK);
	work_add(WORK_COMPACT_CHECK, 1);
	keep = is_cell_empty(node, items->entries[idx].cell_idx)
		&& is_valid_value(node, items->entries[idx].cell_idx,
			items->entries[idx].cell_val);
	work_micro_end(WORK_COMPACT_CHECK);
	return (keep);
}

static void	move_cache_entry(t_order_items *items, int target, int source)
{
	work_micro_begin(WORK_COMPACT_MOVE);
	work_add(WORK_COMPACT_MOVE, 1);
	items->entries[target] = items->entries[source];
	items->meta[target] = items->meta[source];
	work_micro_end(WORK_COMPACT_MOVE);
}

void	compact_cache_entries(t_node_state *node, t_node_order *cache)
{
	int	read_idx;
	int	write_idx;

	write_idx = 0;
	read_idx = 0;
	while (read_idx < cache->items.count)
	{
		if (cache_entry_valid(node, &cache->items, read_idx))
		{
			if (write_idx != read_idx)
				move_cache_entry(&cache->items, write_idx, read_idx);
			write_idx++;
		}
		read_idx++;
	}
	cache->items.count = write_idx;
}
