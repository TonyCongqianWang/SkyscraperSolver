/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_lookahead.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/24 22:52:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_lookahead.h"
#include "node_selection_transition.h"
#include "pruning_routines.h"
#include "pruning_configs.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "grid_interface.h"
#include "node_selection_cache.h"
#include "strategy_routing.h"
#include "selectivity.h"

void	prune_lookahead(t_puzzle *puzzle, t_lookahead_config *config)
{
	t_prune_routine_cfg	cfg;

	init_prune_cfg(&cfg, SELECTIVITY_VALUE_SET);
	cfg.lookahead = *config;
	run_pruning_routine(puzzle, &cfg, 1);
}

static void	probe_and_prune_candidate(t_puzzle *puzzle,
				t_node_transition next, const t_lookahead_config *cfg,
				t_lookahead_pass pass)
{
	t_probe_result	result;

	if (pass == LOOKAHEAD_NEG)
		result = probe_exclusion(puzzle, next, cfg->max_depth, g_check_constr);
	else
		result = probe_assumption(puzzle, next, cfg->max_depth,
				cfg->check_mode);
	if (result.status == DIVE_PASS)
		node_order_record_probe(puzzle->cur_node->order_cache, next,
			pass, result.remaining_entropy);
	if (result.status != DIVE_FAIL)
		return ;
	if (pass == LOOKAHEAD_NEG)
		set_cell_val(puzzle, next.cell_idx, next.cell_val, g_check_constr);
	else
		set_cell_invalid(puzzle, next.cell_idx, next.cell_val,
			g_check_constr);
}

void	probe_candidates(t_puzzle *puzzle, t_node_transition *tr,
			const t_lookahead_config *config, t_lookahead_pass pass)
{
	init_node_transition(tr);
	while (try_get_next_transition(puzzle, tr))
		probe_and_prune_candidate(puzzle, *tr, config, pass);
}
