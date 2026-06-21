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
#include "prune_check_constr.h"
#include "node_selection_cache.h"
#include <stddef.h>

void	get_prune_cfg_light(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = SELECTIVITY_NONE;
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
	cfg->lookahead.selectivity = SELECTIVITY_NONE;
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
	cfg->lookahead.selectivity = SELECTIVITY_NONE;
	cfg->lookahead.max_depth = 1;
}

static void	run_lookahead_loop(t_puzzle *puzzle, t_node_state *node,
				t_selectivity_level selectivity, int max_depth)
{
	t_node_transition	tr;
	t_lookahead_ctx		ctx;
	int					i;
	int					cell_idx;

	node->is_in_lookahead_select = 1;
	node->lookahead_selectivity = selectivity;
	ctx.curr_pass = 1;
	ctx.curr_index = node->lowest_empty_idx;
	i = 0;
	while (i < node->order_cache->count)
	{
		cell_idx = node->order_cache->entries[i].cell_idx;
		ctx.cell_passes[cell_idx] = get_cell_priority_pass(node, cell_idx,
				puzzle->size);
		i++;
	}
	node->lookahead_ctx = &ctx;
	init_node_transition(&tr);
	while (try_get_next_transition(puzzle, &tr))
	{
		if (!do_l_ahead_dive(puzzle, tr, max_depth))
			set_value_invalid(node, tr.cell_idx, tr.cell_val);
	}
	node->lookahead_ctx = NULL;
	node->is_in_lookahead_select = 0;
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
