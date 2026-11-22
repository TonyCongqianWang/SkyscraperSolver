/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_helper.c                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 11:03:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 18:50:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "work_instrumentation.h"
#include "node_selection_cache.h"
#include "grid_availability.h"
#include "node_selection_score.h"
#include "node_selection_transition.h"

static void	add_transition(t_node_order *cache, int cv)
{
	t_node_transition	tr;
	int					c;
	int					v;

	init_node_transition(&tr);
	c = cv >> 8;
	v = cv & 0xFF;
	tr.cell_idx = c;
	tr.cell_val = v;
	cache->items.entries[cache->items.count] = tr;
	cache->items.meta[cache->items.count].cached_br_score = tr.score;
	cache->items.meta[cache->items.count].entropy_pos = -1;
	cache->items.meta[cache->items.count].entropy_neg = -1;
	cache->items.count++;
}

void	collect_cache_entries(t_solver_state *puzzle, t_node_order *cache,
			t_node_select_config *config)
{
	int				i;
	int				c;
	int				v;
	t_node_state	*state;

	(void)config;
	state = puzzle->cur_node;
	cache->items.count = 0;
	i = 0;
	while (i < puzzle->squared_size)
	{
		c = puzzle->cell_distance_order[i];
		if (is_cell_empty(state, c))
		{
			v = puzzle->size;
			while (v >= 1)
			{
				work_add(WORK_CACHE_BUILD_CHECK, 1);
				if (is_valid_value(state, c, v))
					add_transition(cache, (c << 8) | v);
				v--;
			}
		}
		i++;
	}
}
