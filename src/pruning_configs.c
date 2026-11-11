/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pruning_configs.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/26 11:52:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 11:52:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pruning_configs.h"
#include "params_math.h"
#include "params_int.h"
#include "entropy.h"
#include "params_depth_arrays.h"

t_probe_depth	get_probe_depth(int tier, int nesting)
{
	t_probe_depth	depth;

	depth.positive = 0;
	depth.negative = 0;
	if (nesting < MAX_LOOKAHEAD_DEPTH)
		depth = g_probe_depths[nesting][tier];
	return (depth);
}

void	init_prune_cfg(t_prune_routine_cfg *cfg, int tier, int nesting,
		int size)
{
	cfg->selectivity = get_prune_tier_selectivity(tier);
	cfg->check_constr_min_entropy = 0.35;
	cfg->check_constr_max_entropy = 0.70;
	cfg->check_constr_global_min_entropy
		= calc_effective_global_min_entropy(g_initial_constr_global_min_entropy,
			size);
	cfg->lookahead.depth = get_probe_depth(tier, nesting);
	cfg->lookahead.passes = LOOKAHEAD_BOTH;
	cfg->lookahead.check_mode = g_check_constr;
}

t_selectivity_level	get_prune_tier_selectivity(int tier)
{
	if (tier == PRUNE_LIGHT)
		return (SELECTIVITY_VALUE_SET);
	if (tier == PRUNE_MEDIUM)
		return (SELECTIVITY_ANY_CHANGE);
	return (SELECTIVITY_NONE);
}

int	calc_effective_global_min_entropy(int base_entropy, int size)
{
	double	factor;

	factor = get_global_entropy_multiplier(size)
		* compute_max_entropy(size) / 1000000.0;
	return (schedule_int(base_entropy * factor));
}
