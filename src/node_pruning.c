/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_pruning.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_pruning.h"
#include "grid_manipulation.h"
#include "strategy_routing.h"
#include "prune_lookahead.h"
#include "prune_gac.h"

#ifndef FORCE_INVALIDATE_CACHE
# define FORCE_INVALIDATE_CACHE 0
#endif

void	prune_node(t_puzzle *puzzle)
{
	t_prune_config	config;

	if (FORCE_INVALIDATE_CACHE)
	{
		puzzle->cur_node->order_caches[0]->last_build_prog = 0;
		puzzle->cur_node->order_caches[1]->last_build_prog = 0;
		puzzle->cur_node->order_caches[2]->last_build_prog = 0;
	}
	select_prune_config(puzzle, &config);
	if (config.strategy == PRUNE_NONE)
		return ;
	if (config.strategy == PRUNE_LOOKAHEAD_DIVE
		|| config.strategy == PRUNE_HYBRID)
		prune_lookahead(puzzle, &config.lookahead);
	if (config.strategy == PRUNE_GAC || config.strategy == PRUNE_HYBRID)
		prune_gac(puzzle, &config.gac);
	puzzle->cur_node->last_prune_nunset = puzzle->cur_node->num_unset;
	puzzle->cur_node->last_prune_prog = puzzle->cur_node->progress_counter;
	puzzle->cur_node->rows_changed_since_prune = 0;
	puzzle->cur_node->cols_changed_since_prune = 0;
	if (FORCE_INVALIDATE_CACHE)
	{
		puzzle->cur_node->order_caches[0]->last_build_prog = 0;
		puzzle->cur_node->order_caches[1]->last_build_prog = 0;
		puzzle->cur_node->order_caches[2]->last_build_prog = 0;
	}
}
