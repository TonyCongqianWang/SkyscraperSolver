/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_initial.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_initial.h"
#include "prune_check_constr.h"
#include "prune_gac.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "grid_manipulation.h"

static void	prune_initial_step(t_puzzle *puzzle)
{
	t_gac_config		gac_cfg;
	t_node_transition	tr;

	prune_check_constr(puzzle);
	gac_cfg.selectivity = SELECTIVITY_NONE;
	gac_cfg.max_k = 3;
	gac_cfg.analyse_naked = 1;
	gac_cfg.analyse_hidden = 1;
	prune_gac(puzzle, &gac_cfg);
	puzzle->cur_node->is_in_lookahead_select = 1;
	puzzle->cur_node->lookahead_selectivity = SELECTIVITY_NONE;
	init_node_transition(&tr);
	while (try_get_next_transition(puzzle, &tr))
	{
		if (!do_l_ahead_dive(puzzle, tr, 1))
			set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
	}
	puzzle->cur_node->is_in_lookahead_select = 0;
}

void	prune_initial(t_puzzle *puzzle)
{
	t_prune_prog	prev_prog;
	int				prev_num_unset;

	while (1)
	{
		prev_prog = puzzle->cur_node->progress_counter;
		prev_num_unset = puzzle->cur_node->num_unset;
		prune_initial_step(puzzle);
		puzzle->cur_node->last_prune_nunset = prev_num_unset;
		puzzle->cur_node->last_prune_prog = prev_prog;
		puzzle->cur_node->rows_changed_since_prune = 0;
		puzzle->cur_node->cols_changed_since_prune = 0;
		puzzle->cur_node->rows_invalid_since_prune = 0;
		puzzle->cur_node->cols_invalid_since_prune = 0;
		if (puzzle->cur_node->is_invalid || puzzle->cur_node->is_complete)
			break ;
		if (puzzle->cur_node->progress_counter == prev_prog)
			break ;
	}
}
