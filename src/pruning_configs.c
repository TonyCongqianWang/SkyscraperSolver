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

t_probe_depth	get_probe_depth(int tier, int nesting)
{
	t_probe_depth	depth;

	depth.positive = 0;
	depth.negative = 0;
	if (nesting < MAX_LOOKAHEAD_DEPTH)
		depth = g_probe_depths[nesting][tier];
	return (depth);
}

void	init_prune_cfg(t_prune_routine_cfg *cfg, int tier, int nesting)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = get_prune_tier_selectivity(tier);
	cfg->check_constr_min_entropy = 0.35;
	cfg->check_constr_max_entropy = 0.70;
	cfg->check_constr_global_min_entropy = 1283850;
	cfg->run_gac = 0;
	cfg->gac.selectivity = cfg->check_constr_selectivity;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->gac.min_entropy = 0.35;
	cfg->gac.max_entropy = 0.70;
	cfg->gac.global_min_entropy = 1283850;
	cfg->lookahead.selectivity = cfg->check_constr_selectivity;
	cfg->lookahead.depth = get_probe_depth(tier, nesting);
	cfg->run_lookahead = (cfg->lookahead.depth.positive > 0
			|| cfg->lookahead.depth.negative > 0);
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

int	calc_effective_global_min_entropy(int base_entropy, int num_unset, int size)
{
	double	bias;
	double	factor;

	bias = get_global_entropy_unset_bias(size);
	factor = (bias + 50.0) / (bias + (double)num_unset);
	return ((int)(base_entropy * factor));
}
