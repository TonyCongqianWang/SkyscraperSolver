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
#include "pruning_routines.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "grid_interface.h"
#include "node_selection_cache.h"
#include "strategy_routing.h"
#include "selectivity.h"
#include <stddef.h>

void	prune_lookahead(t_puzzle *puzzle, t_lookahead_config *config)
{
	t_prune_routine_cfg	cfg;

	get_prune_cfg_light(&cfg);
	cfg.lookahead = *config;
	run_pruning_routine(puzzle, &cfg, 1);
}

static void	run_lookahead_transitions(t_puzzle *puzzle,
				t_node_transition *tr, int max_depth, t_check_mode mode)
{
	init_node_transition(tr);
	while (try_get_next_transition(puzzle, tr))
	{
		if (!do_l_ahead_dive(puzzle, *tr, max_depth, mode))
			set_cell_invalid(puzzle, tr->cell_idx, tr->cell_val,
				CHECK_CONSTR);
	}
}

static void	init_lookahead_ctx(t_node_state *node, t_lookahead_ctx *ctx,
				int size)
{
	int	i;

	ctx->curr_pass = 1;
	ctx->curr_index = node->lowest_empty_idx;
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

	if (should_exit_selectivity(node, config->selectivity))
		return ;
	node->is_in_lookahead_select = 1;
	node->lookahead_selectivity = config->selectivity;
	select_node_select_config(puzzle, &ns_cfg);
	ns_cfg.selectivity = config->selectivity;
	rebuild_cache_if_stale(puzzle, &ns_cfg, 1);
	init_lookahead_ctx(node, &ctx, puzzle->size);
	node->lookahead_ctx = &ctx;
	run_lookahead_transitions(puzzle, &tr, config->max_depth,
		config->check_mode);
	node->lookahead_ctx = NULL;
	node->is_in_lookahead_select = 0;
}
