/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pruning_routines.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/20 23:59:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/20 23:59:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pruning_routines.h"
#include "prune_gac.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "grid_manipulation.h"

void	get_prune_cfg_light(t_prune_routine_config *cfg)
{
	cfg->run_check_constr = 0;
	cfg->run_gac = 0;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->lookahead.max_depth = 1;
}

void	get_prune_cfg_medium(t_prune_routine_config *cfg)
{
	cfg->run_check_constr = 0;
	cfg->run_gac = 1;
	cfg->gac.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->gac.max_k = 2;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_NONE;
	cfg->lookahead.max_depth = 1;
}

void	get_prune_cfg_heavy(t_prune_routine_config *cfg)
{
	cfg->run_check_constr = 0;
	cfg->run_gac = 1;
	cfg->gac.selectivity = SELECTIVITY_NONE;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_NONE;
	cfg->lookahead.max_depth = 1;
}

void	run_pruning_routine(t_puzzle *puzzle, const t_prune_routine_config *config)
{
	t_node_transition	tr;
	t_node_state		*node;
	t_prune_prog		prev_prog;
	int					prev_num_unset;

	puzzle->prune_runs_count++;
	node = puzzle->cur_node;
	prev_prog = node->progress_counter;
	prev_num_unset = node->num_unset;
	if (config->run_check_constr)
	{
		node->is_in_lookahead_select = 1;
		node->lookahead_selectivity = SELECTIVITY_NONE;
		init_node_transition(&tr);
		while (try_get_next_transition(puzzle, &tr))
		{
			if (!do_l_ahead_dive(puzzle, tr, 0))
				set_value_invalid(node, tr.cell_idx, tr.cell_val);
		}
		node->is_in_lookahead_select = 0;
	}
	if (config->run_gac)
		prune_gac(puzzle, (t_gac_config *)&config->gac);
	if (config->run_lookahead)
	{
		node->is_in_lookahead_select = 1;
		node->lookahead_selectivity = config->lookahead.selectivity;
		init_node_transition(&tr);
		while (try_get_next_transition(puzzle, &tr))
		{
			if (!do_l_ahead_dive(puzzle, tr, config->lookahead.max_depth))
				set_value_invalid(node, tr.cell_idx, tr.cell_val);
		}
		node->is_in_lookahead_select = 0;
	}
	node->last_prune_nunset = prev_num_unset;
	node->last_prune_prog = prev_prog;
	node->rows_changed_since_prune = 0;
	node->cols_changed_since_prune = 0;
	node->rows_invalid_since_prune = 0;
	node->cols_invalid_since_prune = 0;
}
