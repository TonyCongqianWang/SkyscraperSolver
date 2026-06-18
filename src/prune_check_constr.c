/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_check_constr.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "grid_manipulation.h"

void	prune_check_constr(t_puzzle *puzzle)
{
	t_node_transition	tr;

	puzzle->cur_node->is_in_lookahead_select = 1;
	puzzle->cur_node->is_selective_lookahead = 0;
	init_node_transition(&tr);
	while (try_get_next_transition(puzzle, &tr))
	{
		if (!do_l_ahead_dive(puzzle, tr, 0))
			set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
	}
	puzzle->cur_node->is_in_lookahead_select = 0;
}
