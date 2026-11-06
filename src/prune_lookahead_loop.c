/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_lookahead_loop.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/05 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/05 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_lookahead.h"
#include "strategy_routing.h"
#include "node_selection_cache.h"
#include "selectivity.h"

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

static void	prepare_lookahead_cache(t_puzzle *puzzle,
				const t_lookahead_config *config)
{
	t_node_select_config	ns_cfg;

	select_node_select_config(puzzle, &ns_cfg);
	ns_cfg.selectivity = config->selectivity;
	rebuild_cache_if_stale(puzzle, &ns_cfg, 1);
}

static void	execute_lookahead(t_puzzle *puzzle,
				t_node_state *node, const t_lookahead_config *config,
				t_lookahead_pass passes)
{
	t_node_transition		tr;
	t_lookahead_ctx			ctx;
	t_lookahead_ctx			*prev_ctx;
	t_selectivity_level		prev_selectivity;
	int						prev_selecting;

	prev_ctx = node->lookahead_ctx;
	prev_selectivity = node->lookahead_selectivity;
	prev_selecting = node->is_in_lookahead_select;
	node->is_in_lookahead_select = 1;
	node->lookahead_selectivity = config->selectivity;
	prepare_lookahead_cache(puzzle, config);
	init_lookahead_ctx(node, &ctx, puzzle->size);
	node->lookahead_ctx = &ctx;
	if (passes & LOOKAHEAD_POS)
		probe_candidates(puzzle, &tr, config, LOOKAHEAD_POS);
	if (passes & LOOKAHEAD_NEG)
		probe_candidates(puzzle, &tr, config, LOOKAHEAD_NEG);
	node->lookahead_ctx = prev_ctx;
	node->is_in_lookahead_select = prev_selecting;
	node->lookahead_selectivity = prev_selectivity;
}

void	run_lookahead(t_puzzle *puzzle, t_node_state *node,
			const t_lookahead_config *config)
{
	t_lookahead_pass	passes;

	if (should_exit_selectivity(node, config->selectivity))
		return ;
	passes = config->passes;
	if (node->is_in_neg_lookahead)
		passes &= ~LOOKAHEAD_NEG;
	if (passes == LOOKAHEAD_NONE)
		return ;
	execute_lookahead(puzzle, node, config, passes);
	if (node->sub_node_depth == 0 && passes == LOOKAHEAD_BOTH)
	{
		node->order_cache->lookahead_build_entropy
			= node->remaining_entropy;
		node->order_cache->needs_rebuild = 1;
	}
}
