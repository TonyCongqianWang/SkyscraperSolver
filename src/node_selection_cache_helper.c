/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_helper.c                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 11:03:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 11:03:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

int	check_sel_filter(t_node_state *node, int cell_idx,
		int size, int is_selective)
{
	if (!node->is_in_lookahead_select || !is_selective)
		return (1);
	return ((node->rows_changed_since_prune & (1 << (cell_idx / size)))
		|| (node->cols_changed_since_prune & (1 << (cell_idx % size))));
}

int	resume_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_order *cache, int *i_out)
{
	int	i;

	if (next->cell_idx < 0)
	{
		*i_out = cache->lowest_valid_idx;
		return (0);
	}
	i = cache->lowest_valid_idx;
	while (i < cache->count && cache->entries[i].cell_idx != next->cell_idx)
		i++;
	if (i < cache->count)
	{
		next->cell_val++;
		if (set_next_valid_val(puzzle, next)
			&& is_cell_empty(puzzle->cur_node, next->cell_idx))
		{
			*i_out = i;
			return (1);
		}
		i++;
	}
	*i_out = i;
	return (0);
}
