/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_deep.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_deep.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "grid_manipulation.h"

void	prune_deep(t_puzzle *puzzle)
{
	t_node_transition	tr;

	puzzle->cur_node->is_in_lookahead_select = 1;
	puzzle->cur_node->lookahead_selectivity = SELECTIVITY_ANY_CHANGE;
	init_node_transition(&tr);
	while (try_get_next_transition(puzzle, &tr))
	{
		if (!do_l_ahead_dive(puzzle, tr, 1))
			set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
	}
	puzzle->cur_node->is_in_lookahead_select = 0;
}

int	should_skip_prune_deep(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			unset_ratio;
	double			x;
	t_prune_prog	period;

	node = puzzle->cur_node;
	if (node->num_unset == 0)
		return (1);
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	if (unset_ratio < 0.3)
		return (1);
	x = 1 - unset_ratio;
	period = (t_prune_prog)(30 + 40 * x + 60 * x * x + 100 * x * x * x);
	return (node->progress_counter < node->last_prune_prog + period);
}
