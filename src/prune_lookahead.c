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

	get_prune_cfg_light(&cfg);
	cfg.lookahead = *config;
	run_pruning_routine(puzzle, &cfg, 1);
}

static void	run_dive_transitions(t_puzzle *puzzle, t_node_transition *tr,
				const t_lookahead_config *config, int is_neg)
{
	int	result;

	init_node_transition(tr);
	while (try_get_next_transition(puzzle, tr))
	{
		if (is_neg)
		{
			result = do_l_ahead_dive_neg(puzzle, *tr, config->max_depth,
					g_check_constr);
			if (result == 0)
				set_cell_val(puzzle, tr->cell_idx, tr->cell_val,
					g_check_constr);
		}
		else if (!do_l_ahead_dive(puzzle, *tr, config->max_depth,
					config->check_mode))
			set_cell_invalid(puzzle, tr->cell_idx, tr->cell_val,
				g_check_constr);
	}
}

static void	run_lookahead_transitions(t_puzzle *puzzle,
				t_node_transition *tr, const t_lookahead_config *config)
{
	if (config->lookahead_side != LOOKAHEAD_SIDE_NEG)
		run_dive_transitions(puzzle, tr, config, 0);
	if (config->lookahead_side != LOOKAHEAD_SIDE_POS
		&& !puzzle->cur_node->is_in_neg_lookahead)
		run_dive_transitions(puzzle, tr, config, 1);
}

static void	init_lookahead_ctx(t_node_state *node, t_lookahead_ctx *ctx,
				int size)
{
	int	i;

	ctx->curr_pass = 1;
	ctx->curr_index = 0;
	i = -1;
	while (++i < node->order_cache->count)
	{
		ctx->cell_passes[node->order_cache->entries[i].cell_idx]
			= get_cell_priority_pass(
				node, node->order_cache->entries[i].cell_idx, size);
	}
}

void	run_lookahead_loop(t_puzzle *puzzle, t_node_state *node,
			const t_lookahead_config *config)
{
	t_node_transition		tr;
	t_lookahead_ctx			ctx;
	t_node_select_config	ns_cfg;
	t_lookahead_ctx		*prev_ctx;
	t_selectivity_level	prev_selectivity;
	int					prev_selecting;

	if (should_exit_selectivity(node, config->selectivity))
		return ;
	prev_ctx = node->lookahead_ctx;
	prev_selectivity = node->lookahead_selectivity;
	prev_selecting = node->is_in_lookahead_select;
	node->is_in_lookahead_select = 1;
	node->lookahead_selectivity = config->selectivity;
	select_node_select_config(puzzle, &ns_cfg);
	ns_cfg.selectivity = config->selectivity;
	rebuild_cache_if_stale(puzzle, &ns_cfg, 1);
	init_lookahead_ctx(node, &ctx, puzzle->size);
	node->lookahead_ctx = &ctx;
	run_lookahead_transitions(puzzle, &tr, config);
	node->lookahead_ctx = prev_ctx;
	node->is_in_lookahead_select = prev_selecting;
	node->lookahead_selectivity = prev_selectivity;
	if (!node->is_in_neg_lookahead
		&& (config->lookahead_side == LOOKAHEAD_SIDE_NEG
			|| config->lookahead_side == LOOKAHEAD_SIDE_BOTH))
	{
		node->order_cache->lookahead_build_entropy = node->remaining_entropy;
		node->order_cache->needs_rebuild = 1;
	}
}
