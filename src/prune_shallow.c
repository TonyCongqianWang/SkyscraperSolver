/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_shallow.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_shallow.h"
#include "prune_gac.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "grid_manipulation.h"

void	prune_shallow(t_puzzle *puzzle)
{
	t_gac_config		gac_cfg;
	t_node_transition	tr;

	gac_cfg.is_selective = 1;
	gac_cfg.max_k = 2;
	gac_cfg.analyse_naked = 1;
	gac_cfg.analyse_hidden = 1;
	prune_gac(puzzle, &gac_cfg);
	puzzle->cur_node->is_in_lookahead_select = 1;
	puzzle->cur_node->is_selective_lookahead = 0;
	init_node_transition(&tr);
	while (try_get_next_transition(puzzle, &tr))
	{
		if (!do_l_ahead_dive(puzzle, tr, 1))
			set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
	}
	puzzle->cur_node->is_in_lookahead_select = 0;
}

int	should_skip_prune_shallow(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			unset_ratio;
	t_prune_prog	period;

	node = puzzle->cur_node;
	if (node->num_unset == 0)
		return (1);
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	if (unset_ratio < 0.4)
		return (1);
	period = (t_prune_prog)(46 / unset_ratio);
	return (node->progress_counter < node->last_prune_prog + period);
}
