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

static int	get_probe_depth(int tier, int nesting)
{
	if (nesting >= MAX_LOOKAHEAD_DEPTH)
		return (0);
	return (g_lookahead_probe_depth[nesting][tier]);
}

void	init_prune_cfg(t_prune_routine_cfg *cfg, int tier, int nesting,
		int size)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = get_prune_tier_selectivity(tier);
	cfg->check_constr_min_entropy = 0.35;
	cfg->check_constr_max_entropy = 0.70;
	cfg->check_constr_global_min_entropy
		= calc_effective_global_min_entropy(g_initial_constr_global_min_entropy,
			size);
	cfg->run_gac = 0;
	cfg->gac.selectivity = cfg->check_constr_selectivity;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->gac.min_entropy = 0.35;
	cfg->gac.max_entropy = 0.70;
	cfg->gac.global_min_entropy
		= calc_effective_global_min_entropy(
			g_initial_gac_global_min_entropy, size);
	cfg->lookahead.selectivity = cfg->check_constr_selectivity;
	cfg->lookahead.max_depth = get_probe_depth(tier, nesting);
	cfg->run_lookahead = (cfg->lookahead.max_depth > 0);
	cfg->lookahead.passes = LOOKAHEAD_BOTH;
	cfg->lookahead.check_mode = g_check_constr;
}

t_selectivity_level	get_prune_tier_selectivity(int tier)
{
	if (tier == 0)
		return (SELECTIVITY_VALUE_SET);
	if (tier == 1)
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
