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

extern const int	g_keep_pruning;

static void	apply_prune_config(t_puzzle *puzzle, t_prune_config *config)
{
	if (config->strategy == PRUNE_GAC || config->strategy == PRUNE_HYBRID)
		prune_gac(puzzle, &config->gac);
	if (config->strategy == PRUNE_LOOKAHEAD_DIVE
		|| config->strategy == PRUNE_HYBRID)
		prune_lookahead(puzzle, &config->lookahead);
}

static void	update_pruned_state(t_puzzle *puzzle, int prev_num_unset,
		t_prune_prog prev_prog)
{
	puzzle->cur_node->last_prune_nunset = prev_num_unset;
	puzzle->cur_node->last_prune_prog = prev_prog;
	puzzle->cur_node->rows_changed_since_prune = 0;
	puzzle->cur_node->cols_changed_since_prune = 0;
}

static void	finalize_prune_state(t_puzzle *puzzle)
{
	puzzle->cur_node->last_prune_nunset = puzzle->cur_node->num_unset;
	puzzle->cur_node->last_prune_prog = puzzle->cur_node->progress_counter;
}

void	prune_node(t_puzzle *puzzle)
{
	t_prune_config	config;
	t_prune_prog	prev_prog;
	int				prev_num_unset;
	int				pruned;

	pruned = 0;
	while (1)
	{
		select_prune_config(puzzle, &config);
		if (config.strategy == PRUNE_NONE)
			break ;
		pruned = 1;
		prev_prog = puzzle->cur_node->progress_counter;
		prev_num_unset = puzzle->cur_node->num_unset;
		apply_prune_config(puzzle, &config);
		update_pruned_state(puzzle, prev_num_unset, prev_prog);
		if (!g_keep_pruning || puzzle->cur_node->progress_counter == prev_prog)
			break ;
	}
	if (pruned)
		finalize_prune_state(puzzle);
}
