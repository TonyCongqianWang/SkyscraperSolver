/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_lookahead.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_lookahead.h"
#include "grid_manipulation.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "node_selection_cache.h"
#include "strategy_routing.h"

void	prune_lookahead(t_puzzle *puzzle, t_lookahead_config *config)
{
	t_node_transition		tr;

	puzzle->cur_node->is_in_lookahead_select = 1;
	puzzle->cur_node->is_selective_lookahead = config->is_selective;
	init_node_transition(&tr);
	while (try_get_next_transition(puzzle, &tr))
	{
		if (!do_l_ahead_dive(puzzle, tr, config->max_depth))
			set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
	}
	puzzle->cur_node->is_in_lookahead_select = 0;
}
