/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_cfg_setup.c                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_cfg_setup.h"
#include "pruning_configs.h"

void	setup_cfg_thresholds(t_prune_routine_cfg *cfg,
			const t_prune_limits *lim, int remaining_entropy)
{
	cfg->run_gac = (remaining_entropy >= lim->gac_min_entropy);
	cfg->run_check_constr = (remaining_entropy >= lim->constr_min_entropy);
	cfg->lookahead.check_mode.run_constr = 1;
	cfg->lookahead.check_mode.run_gac = 1;
	cfg->lookahead.check_mode.run_prop = 1;
	cfg->lookahead.check_mode.lookahead_continue_min_entropy
		= lim->lh_continue_min_entropy;
	cfg->lookahead.check_mode.lookahead_continue_slope
		= lim->lh_continue_slope;
}

void	setup_cfg_bounds(t_prune_routine_cfg *cfg,
			const t_prune_limits *lim, int num_unset, int size)
{
	cfg->gac.min_entropy = lim->gac_local_min_entropy;
	cfg->gac.max_entropy = lim->gac_local_max_entropy;
	cfg->gac.global_min_entropy
		= calc_effective_global_min_entropy(lim->gac_global_min_entropy,
			num_unset, size);
	cfg->check_constr_min_entropy = lim->constr_local_min_entropy;
	cfg->check_constr_max_entropy = lim->constr_local_max_entropy;
	cfg->check_constr_global_min_entropy
		= calc_effective_global_min_entropy(lim->constr_global_min_entropy,
			num_unset, size);
	cfg->lookahead.check_mode.constr.min_entropy
		= lim->lh_constr_local_min_entropy;
	cfg->lookahead.check_mode.constr.max_entropy
		= lim->lh_constr_local_max_entropy;
	cfg->lookahead.check_mode.constr.global_min_entropy
		= calc_effective_global_min_entropy(
			lim->lh_constr_global_min_entropy, num_unset, size);
	cfg->lookahead.check_mode.gac.min_entropy
		= lim->lh_gac_local_min_entropy;
	cfg->lookahead.check_mode.gac.max_entropy
		= lim->lh_gac_local_max_entropy;
	cfg->lookahead.check_mode.gac.global_min_entropy
		= calc_effective_global_min_entropy(
			lim->lh_gac_global_min_entropy, num_unset, size);
}
