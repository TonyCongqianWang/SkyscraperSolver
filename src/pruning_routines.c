/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pruning_routines.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/20 23:59:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pruning_routines.h"
#include "pruning_configs.h"
#include "prune_gac.h"
#include "prune_lookahead.h"
#include "prune_check_constr.h"
#include "selectivity.h"
#include <stddef.h>

static void	run_check_constr_routine(t_puzzle *puzzle,
				const t_prune_routine_cfg *cfg)
{
	t_constr_limits	limits;

	limits.min_unset = cfg->check_constr_min_unset;
	limits.max_unset = cfg->check_constr_max_unset;
	limits.global_min_entropy = cfg->check_constr_global_min_entropy;
	prune_check_constr(puzzle, cfg->check_constr_selectivity, &limits);
}

static int	check_early_skips(t_node_state *node,
				const t_prune_routine_cfg *cfg, int cfg_idx)
{
	int	only_val_set;
	int	i;

	only_val_set = is_only_selectivity_value_set(cfg);
	if (only_val_set && node->rows_changed_since_prune == 0
		&& node->cols_changed_since_prune == 0)
	{
		i = -1;
		while (++i <= cfg_idx)
			node->last_entropy[i] = node->remaining_entropy;
		return (1);
	}
	if (is_max_selectivity_any_change(cfg)
		&& node->rows_changed_since_prune == 0
		&& node->cols_changed_since_prune == 0
		&& node->rows_invalid_since_prune == 0
		&& node->cols_invalid_since_prune == 0)
	{
		i = -1;
		while (++i <= cfg_idx)
			node->last_entropy[i] = node->remaining_entropy;
		return (1);
	}
	return (0);
}

static void	post_prune_update(t_node_state *node, int prev_num_unset,
				int only_val_set)
{
	node->last_prune_nunset = prev_num_unset;
	node->rows_changed_since_prune = 0;
	node->cols_changed_since_prune = 0;
	if (!only_val_set)
	{
		node->rows_invalid_since_prune = 0;
		node->cols_invalid_since_prune = 0;
	}
}

int	run_pruning_routine(t_puzzle *puzzle, const t_prune_routine_cfg *cfg,
		int cfg_idx)
{
	t_node_state	*node;
	int				prev_entropy;
	int				i;

	node = puzzle->cur_node;
	if (check_early_skips(node, cfg, cfg_idx))
		return (0);
	puzzle->prune_runs_count++;
	prev_entropy = node->remaining_entropy;
	if (cfg->run_check_constr)
		run_check_constr_routine(puzzle, cfg);
	if (cfg->run_gac)
		prune_gac(puzzle, (t_gac_config *)&cfg->gac);
	if (cfg->run_lookahead)
		run_lookahead_loop(puzzle, node, &cfg->lookahead);
	i = -1;
	while (++i <= cfg_idx)
		node->last_entropy[i] = prev_entropy;
	post_prune_update(node, node->num_unset,
		is_only_selectivity_value_set(cfg));
	if (node->remaining_entropy == prev_entropy)
		return (0);
	return (1);
}
