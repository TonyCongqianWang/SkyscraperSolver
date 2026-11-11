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

static void	run_check_constr_routine(t_solver_state *puzzle,
				const t_prune_routine_cfg *cfg)
{
	t_constr_limits	limits;

	limits.min_entropy = cfg->check_constr_min_entropy;
	limits.max_entropy = cfg->check_constr_max_entropy;
	limits.global_min_entropy = cfg->check_constr_global_min_entropy;
	prune_check_constr(puzzle, cfg->selectivity, &limits);
}

static void	post_prune_update(t_node_state *node,
				t_selectivity_level selectivity)
{
	node->rows_changed_since_prune = 0;
	node->cols_changed_since_prune = 0;
	if (selectivity != SELECTIVITY_VALUE_SET)
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
	prev_entropy = node->domain.remaining_entropy;
	if (!should_exit_selectivity(node, cfg->selectivity))
	{
		puzzle->prune_runs_count++;
		if (prev_entropy >= cfg->check_constr_global_min_entropy)
			run_check_constr_routine(puzzle, cfg);
		run_lookahead(puzzle, &cfg->lookahead, cfg->selectivity);
		post_prune_update(node, cfg->selectivity);
	}
	i = -1;
	while (++i <= cfg_idx)
		node->last_entropy[i] = prev_entropy;
	return (1);
}
