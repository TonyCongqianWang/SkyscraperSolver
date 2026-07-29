/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_api.c                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/19 19:35:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 19:15:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_transition.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

#ifndef USE_CONSTRS_SCORING
# define USE_CONSTRS_SCORING 0
#endif

int	get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_state	*node;
	int				i;

	node = puzzle->cur_node;
	i = 0;
	while (i < node->order_cache->count)
	{
		if (is_cell_empty(node, node->order_cache->entries[i].cell_idx)
			&& is_valid_value(node, node->order_cache->entries[i].cell_idx,
				node->order_cache->entries[i].cell_val))
		{
			*next = node->order_cache->entries[i];
			return (1);
		}
		i++;
	}
	(void)config;
	return (0);
}
