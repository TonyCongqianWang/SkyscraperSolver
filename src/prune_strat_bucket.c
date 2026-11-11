/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_bucket.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/03 14:30:00 by towang            #+#    #+#             */
/*   Updated: 2026/09/03 14:30:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_bucket.h"
#include "prune_strat_cfg_setup.h"
#include "pruning_routines.h"
#include "pruning_configs.h"
#include "entropy.h"
#include "math_utils.h"
#include "params_depth_arrays.h"

static void	populate_limits(t_prune_limits *lim, int b)
{
	lim->lh_continue_min_entropy = g_depth_lookahead_continue_min_entropy[b];
	lim->lh_continue_slope = g_depth_lookahead_continue_slope[b];
	lim->constr_local_min_entropy = g_depth_constr_local_min_entropy[b];
	lim->constr_local_max_entropy = g_depth_constr_local_max_entropy[b];
	lim->constr_global_min_entropy = g_depth_constr_global_min_entropy[b];
	lim->lh_constr_local_min_entropy
		= g_depth_lookahead_constr_local_min_entropy[b];
	lim->lh_constr_local_max_entropy
		= g_depth_lookahead_constr_local_max_entropy[b];
	lim->lh_constr_global_min_entropy
		= g_depth_lookahead_constr_global_min_entropy[b];
}

static int	run_tier(t_solver_state *puzzle, int tier, int remaining_entropy,
				int b)
{
	t_prune_routine_cfg	cfg;
	t_prune_limits		lim;

	init_prune_cfg(&cfg, tier, puzzle->cur_node->tree.lookahead_depth,
		puzzle->size);
	populate_limits(&lim, b);
	setup_scheduled_prune_cfg(&cfg, &lim, puzzle->size, remaining_entropy);
	return (run_pruning_routine(puzzle, &cfg, tier));
}

static double	calc_period(t_solver_state *puzzle, t_node_state *node, int b)
{
	double	raw;
	int		rem;

	rem = node->domain.remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem) / rem;
	return (g_depth_period_coef_scale[b] * dpow075_approx(raw)
		+ g_depth_period_coef_unset[b]
		* (puzzle->squared_size - node->domain.num_unset));
}

int	prune_strat_depth_bucket(t_solver_state *puzzle, int b)
{
	t_node_state	*node;
	double			period;
	int				tier;

	node = puzzle->cur_node;
	if (node->domain.is_invalid || node->domain.is_complete
		|| node->domain.num_unset == 0
		|| node->domain.remaining_entropy < g_depth_min_entropy[b])
		return (0);
	period = calc_period(puzzle, node, b);
	tier = select_prune_tier(node, period,
			g_depth_period_tier_medium_mult[b],
			g_depth_period_tier_heavy_mult[b]);
	if (tier < 0)
		return (0);
	return (run_tier(puzzle, tier, node->domain.remaining_entropy, b));
}
