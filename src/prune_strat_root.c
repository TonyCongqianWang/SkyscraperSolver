/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_root.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_root.h"
#include "prune_strat_cfg_setup.h"
#include "pruning_routines.h"
#include "pruning_configs.h"
#include "entropy.h"
#include "math_utils.h"
#include "params_int.h"
#include "params_double.h"

static void	populate_limits(t_prune_limits *lim)
{
	lim->gac_min_entropy = g_root_gac_min_entropy;
	lim->constr_min_entropy = g_root_constr_min_entropy;
	lim->lh_continue_min_entropy = g_root_lookahead_continue_min_entropy;
	lim->lh_continue_slope = g_root_lookahead_continue_slope;
	lim->gac_local_min_entropy = g_root_gac_local_min_entropy;
	lim->gac_local_max_entropy = g_root_gac_local_max_entropy;
	lim->gac_global_min_entropy = g_root_gac_global_min_entropy;
	lim->constr_local_min_entropy = g_root_constr_local_min_entropy;
	lim->constr_local_max_entropy = g_root_constr_local_max_entropy;
	lim->constr_global_min_entropy = g_root_constr_global_min_entropy;
	lim->lh_constr_local_min_entropy
		= g_root_lookahead_constr_local_min_entropy;
	lim->lh_constr_local_max_entropy
		= g_root_lookahead_constr_local_max_entropy;
	lim->lh_constr_global_min_entropy
		= g_root_lookahead_constr_global_min_entropy;
	lim->lh_gac_local_min_entropy
		= g_root_lookahead_gac_local_min_entropy;
	lim->lh_gac_local_max_entropy
		= g_root_lookahead_gac_local_max_entropy;
	lim->lh_gac_global_min_entropy
		= g_root_lookahead_gac_global_min_entropy;
}

static int	run_tier(t_solver_state *puzzle, int tier, int remaining_entropy)
{
	t_prune_routine_cfg	cfg;
	t_prune_limits		lim;

	init_prune_cfg(&cfg, get_prune_tier_selectivity(tier));
	populate_limits(&lim);
	setup_cfg_thresholds(&cfg, &lim, remaining_entropy);
	setup_cfg_bounds(&cfg, &lim, puzzle->cur_node->domain.num_unset,
		puzzle->size);
	return (run_pruning_routine(puzzle, &cfg, tier));
}

static double	calc_period(t_solver_state *puzzle, t_node_state *node)
{
	double	raw;
	int		rem;

	rem = node->domain.remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem) / rem;
	return (g_root_period_coef_scale * dpow075_approx(raw)
		+ g_root_period_coef_unset
		* (puzzle->squared_size - node->domain.num_unset));
}

int	prune_strat_root(t_solver_state *puzzle)
{
	t_node_state	*node;
	double			period;

	node = puzzle->cur_node;
	if (node->domain.is_invalid || node->domain.is_complete
		|| node->domain.num_unset == 0
		|| node->domain.remaining_entropy < g_root_min_entropy)
		return (0);
	period = calc_period(puzzle, node);
	if (node->last_entropy[0] - node->domain.remaining_entropy > period)
		return (run_tier(puzzle, 0, node->domain.remaining_entropy));
	if (node->last_entropy[1] - node->domain.remaining_entropy
		> period * g_root_period_tier_medium_mult)
		return (run_tier(puzzle, 1, node->domain.remaining_entropy));
	if (node->last_entropy[2] - node->domain.remaining_entropy
		> period * g_root_period_tier_heavy_mult)
		return (run_tier(puzzle, 2, node->domain.remaining_entropy));
	return (0);
}
