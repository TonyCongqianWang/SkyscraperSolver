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
#include "prune_lookahead.h"
#include "prune_check_constr.h"
#include "selectivity.h"
#include <stddef.h>

static void	run_check_constr_routine(t_solver_state *puzzle,
				const t_prune_routine_cfg *cfg)
{
	t_constr_limits	limits;

	limits.min_entropy = cfg->check_constr_min_entropy;
	limits.max_entropy = cfg->check_constr_max_entropy;
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
			node->last_entropy[i] = node->domain.remaining_entropy;
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
			node->last_entropy[i] = node->domain.remaining_entropy;
		return (1);
	}
	return (0);
}

static void	post_prune_update(t_node_state *node, int only_val_set)
{
	node->rows_changed_since_prune = 0;
	node->cols_changed_since_prune = 0;
	if (!only_val_set)
	{
		node->rows_invalid_since_prune = 0;
		node->cols_invalid_since_prune = 0;
	}
}

int	run_pruning_routine(t_solver_state *puzzle, const t_prune_routine_cfg *cfg,
		int cfg_idx)
{
	t_node_state	*node;
	int				prev_entropy;
	int				i;

	node = puzzle->cur_node;
	if (check_early_skips(node, cfg, cfg_idx))
		return (1);
	puzzle->prune_runs_count++;
	prev_entropy = node->domain.remaining_entropy;
	if (cfg->run_check_constr)
		run_check_constr_routine(puzzle, cfg);
	if (cfg->run_lookahead)
		run_lookahead(puzzle, node, &cfg->lookahead);
	i = -1;
	while (++i <= cfg_idx)
		node->last_entropy[i] = prev_entropy;
	post_prune_update(node, is_only_selectivity_value_set(cfg));
	return (1);
}
