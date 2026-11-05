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

void	init_prune_cfg(t_prune_routine_cfg *cfg,
			t_selectivity_level selectivity)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = selectivity;
	cfg->check_constr_min_entropy = 0.35;
	cfg->check_constr_max_entropy = 0.70;
	cfg->check_constr_global_min_entropy = 513540;
	cfg->run_gac = 0;
	cfg->gac.selectivity = selectivity;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->gac.min_entropy = 0.35;
	cfg->gac.max_entropy = 0.70;
	cfg->gac.global_min_entropy = 513540;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = selectivity;
	cfg->lookahead.max_depth = 1;
	cfg->lookahead.lookahead_side = LOOKAHEAD_SIDE_POS;
	if (selectivity == SELECTIVITY_NONE)
		cfg->lookahead.lookahead_side = LOOKAHEAD_SIDE_BOTH;
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

int	calc_effective_global_min_entropy(int base_entropy, int num_unset, int size)
{
	double	bias;
	double	factor;

	bias = get_global_entropy_unset_bias(size);
	factor = (bias + 50.0) / (bias + (double)num_unset);
	return ((int)(base_entropy * factor));
}
