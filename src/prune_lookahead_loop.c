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
#include "search_context.h"
#include "tree_search.h"

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

static void	prepare_lookahead_cache(t_solver_state *puzzle,
				const t_lookahead_config *config)
{
	t_node_select_config	ns_cfg;

	select_node_select_config(puzzle, &ns_cfg);
	ns_cfg.selectivity = config->selectivity;
	rebuild_cache_if_stale(puzzle, &ns_cfg, 1);
}

static void	execute_lookahead(t_solver_state *puzzle,
				t_node_state *node, const t_lookahead_config *config,
				t_lookahead_pass passes)
{
	t_lookahead_ctx			ctx;
	t_search_scope			saved;

	enter_lookahead(node, &ctx, config->selectivity, &saved);
	prepare_lookahead_cache(puzzle, config);
	init_lookahead_ctx(node, &ctx, puzzle->size);
	if (passes & LOOKAHEAD_POS)
		run_tree_search(puzzle, config, LOOKAHEAD_POS);
	if (passes & LOOKAHEAD_NEG)
		run_tree_search(puzzle, config, LOOKAHEAD_NEG);
	leave_lookahead(node, &saved);
}

void	run_lookahead(t_solver_state *puzzle, t_node_state *node,
			const t_lookahead_config *config)
{
	t_lookahead_pass	passes;

	if (node->tree.lookahead_depth >= MAX_LOOKAHEAD_DEPTH
		|| should_exit_selectivity(node, config->selectivity))
		return ;
	passes = config->passes;
	if (node->tree.neg_lookahead_depth >= MAX_NEG_LOOKAHEAD_DEPTH)
		passes &= ~LOOKAHEAD_NEG;
	if (passes == LOOKAHEAD_NONE)
		return ;
	execute_lookahead(puzzle, node, config, passes);
	node_order_finish_lookahead(node, passes);
}
