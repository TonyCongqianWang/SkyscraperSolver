/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pruning_routines.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/20 23:59:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/24 22:52:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pruning_routines.h"
#include "prune_gac.h"
#include "prune_lookahead.h"
#include "prune_check_constr.h"
#include <stddef.h>

void	get_prune_cfg_vlight(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->run_gac = 0;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_VALUE_SET;
	cfg->lookahead.max_depth = 1;
}

void	get_prune_cfg_light(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->run_gac = 0;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->lookahead.max_depth = 1;
}

void	get_prune_cfg_medium(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 1;
	cfg->check_constr_selectivity = SELECTIVITY_VALUE_SET;
	cfg->run_gac = 1;
	cfg->gac.selectivity = SELECTIVITY_VALUE_SET;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->lookahead.max_depth = 1;
}

void	get_prune_cfg_heavy(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 1;
	cfg->check_constr_selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->run_gac = 1;
	cfg->gac.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->lookahead.max_depth = 1;
}

void	run_pruning_routine(t_puzzle *puzzle, const t_prune_routine_cfg *cfg)
{
	t_node_state	*node;
	t_prune_prog	prev_prog;
	int				prev_num_unset;

	puzzle->prune_runs_count++;
	node = puzzle->cur_node;
	prev_prog = node->progress_counter;
	prev_num_unset = node->num_unset;
	if (cfg->run_check_constr)
		prune_check_constr(puzzle, cfg->check_constr_selectivity);
	if (cfg->run_gac)
		prune_gac(puzzle, (t_gac_config *)&cfg->gac);
	if (cfg->run_lookahead)
		run_lookahead_loop(puzzle, node, cfg->lookahead.selectivity,
			cfg->lookahead.max_depth);
	node->last_prune_nunset = prev_num_unset;
	node->last_prune_prog = prev_prog;
	node->rows_changed_since_prune = 0;
	node->cols_changed_since_prune = 0;
	node->rows_invalid_since_prune = 0;
	node->cols_invalid_since_prune = 0;
}
