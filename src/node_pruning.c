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

#ifndef KEEP_PRUNING
# define KEEP_PRUNING 0
#endif

void	prune_node(t_puzzle *puzzle)
{
	t_prune_config	config;
	t_prune_prog	prev_prog;

	while (1)
	{
		select_prune_config(puzzle, &config);
		if (config.strategy == PRUNE_NONE)
			break ;
		prev_prog = puzzle->cur_node->progress_counter;
		if (config.strategy == PRUNE_LOOKAHEAD_DIVE
			|| config.strategy == PRUNE_HYBRID)
			prune_lookahead(puzzle, &config.lookahead);
		if (config.strategy == PRUNE_GAC || config.strategy == PRUNE_HYBRID)
			prune_gac(puzzle, &config.gac);
		puzzle->cur_node->last_prune_nunset = puzzle->cur_node->num_unset;
		puzzle->cur_node->last_prune_prog = prev_prog;
		puzzle->cur_node->rows_changed_since_prune = 0;
		puzzle->cur_node->cols_changed_since_prune = 0;
		if (!KEEP_PRUNING || puzzle->cur_node->progress_counter == prev_prog)
			break ;
	}
}
