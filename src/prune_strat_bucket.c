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
#include "params_int.h"
#include "params_double.h"
#include "params_math.h"
#include "params_depth_arrays.h"

int	get_depth_bucket(int depth, int squared_size, int size)
{
	int	i;

	i = 0;
	while (i < 9)
	{
		if (depth <= (int)(squared_size * get_routing_depth_ratio(size, i)))
			return (i);
		i++;
	}
	return (9);
}

static void	populate_limits(t_prune_limits *lim, int b)
{
	lim->gac_min_entropy = *g_depth_gac_min_entropy[b];
	lim->constr_min_entropy = *g_depth_constr_min_entropy[b];
	lim->lh_continue_min_entropy = *g_depth_lookahead_continue_min_entropy[b];
	lim->lh_continue_slope = *g_depth_lookahead_continue_slope[b];
	lim->gac_local_min_entropy = *g_depth_gac_local_min_entropy[b];
	lim->gac_local_max_entropy = *g_depth_gac_local_max_entropy[b];
	lim->gac_global_min_entropy = *g_depth_gac_global_min_entropy[b];
	lim->constr_local_min_entropy = *g_depth_constr_local_min_entropy[b];
	lim->constr_local_max_entropy = *g_depth_constr_local_max_entropy[b];
	lim->constr_global_min_entropy = *g_depth_constr_global_min_entropy[b];
	lim->lh_constr_local_min_entropy
		= *g_depth_lookahead_constr_local_min_entropy[b];
	lim->lh_constr_local_max_entropy
		= *g_depth_lookahead_constr_local_max_entropy[b];
	lim->lh_constr_global_min_entropy
		= *g_depth_lookahead_constr_global_min_entropy[b];
	lim->lh_gac_local_min_entropy
		= *g_depth_lookahead_gac_local_min_entropy[b];
	lim->lh_gac_local_max_entropy
		= *g_depth_lookahead_gac_local_max_entropy[b];
	lim->lh_gac_global_min_entropy
		= *g_depth_lookahead_gac_global_min_entropy[b];
}

static int	run_tier(t_puzzle *puzzle, int tier, int remaining_entropy,
				int b)
{
	t_prune_routine_cfg	cfg;
	t_prune_limits		lim;

	if (tier == 0)
		get_prune_cfg_light(&cfg);
	else if (tier == 1)
		get_prune_cfg_medium(&cfg);
	else
		get_prune_cfg_heavy(&cfg);
	populate_limits(&lim, b);
	setup_cfg_thresholds(&cfg, &lim, remaining_entropy);
	setup_cfg_bounds(&cfg, &lim, puzzle->cur_node->num_unset, puzzle->size);
	return (run_pruning_routine(puzzle, &cfg, tier));
}

static double	calc_period(t_puzzle *puzzle, t_node_state *node, int b)
{
	double	raw;
	int		rem;

	rem = node->remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem) / rem;
	return (*g_depth_period_coef_scale[b] * dpow075_approx(raw)
		+ *g_depth_period_coef_unset[b]
		* (puzzle->squared_size - node->num_unset));
}

int	prune_strat_depth_bucket(t_puzzle *puzzle, int b)
{
	t_node_state	*node;
	double			period;

	node = puzzle->cur_node;
	if (node->is_invalid || node->is_complete || node->num_unset == 0
		|| node->remaining_entropy < *g_depth_min_entropy[b])
		return (0);
	period = calc_period(puzzle, node, b);
	if (node->last_entropy[0] - node->remaining_entropy > period)
		return (run_tier(puzzle, 0, node->remaining_entropy, b));
	if (node->last_entropy[1] - node->remaining_entropy
		> period * *g_depth_period_tier_medium_mult[b])
		return (run_tier(puzzle, 1, node->remaining_entropy, b));
	if (node->last_entropy[2] - node->remaining_entropy
		> period * *g_depth_period_tier_heavy_mult[b])
		return (run_tier(puzzle, 2, node->remaining_entropy, b));
	return (0);
}
