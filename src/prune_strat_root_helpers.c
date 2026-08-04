/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_root_helpers.c                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_root_helpers.h"
#include "pruning_configs.h"
#include "params_int.h"
#include "params_double.h"

void	setup_cfg_thresholds(t_prune_routine_cfg *cfg, int remaining_entropy)
{
	cfg->run_gac = (remaining_entropy >= g_root_gac_min_entropy);
	cfg->run_check_constr = (remaining_entropy >= g_root_constr_min_entropy);
	cfg->lookahead.check_mode.run_constr = 1;
	cfg->lookahead.check_mode.run_gac = 1;
	cfg->lookahead.check_mode.run_prop = 1;
	cfg->lookahead.check_mode.lookahead_continue_min_entropy
		= g_root_lookahead_continue_min_entropy;
	cfg->lookahead.check_mode.lookahead_continue_slope
		= g_root_lookahead_continue_slope;
}

void	setup_cfg_bounds(t_prune_routine_cfg *cfg, int num_unset, int size)
{
	cfg->gac.min_entropy = g_root_gac_local_min_entropy;
	cfg->gac.max_entropy = g_root_gac_local_max_entropy;
	cfg->gac.global_min_entropy
		= calc_effective_global_min_entropy(g_root_gac_global_min_entropy,
			num_unset, size);
	cfg->check_constr_min_entropy = g_root_constr_local_min_entropy;
	cfg->check_constr_max_entropy = g_root_constr_local_max_entropy;
	cfg->check_constr_global_min_entropy
		= calc_effective_global_min_entropy(g_root_constr_global_min_entropy,
			num_unset, size);
	cfg->lookahead.check_mode.constr.min_entropy
		= g_root_lookahead_constr_local_min_entropy;
	cfg->lookahead.check_mode.constr.max_entropy
		= g_root_lookahead_constr_local_max_entropy;
	cfg->lookahead.check_mode.constr.global_min_entropy
		= calc_effective_global_min_entropy(
			g_root_lookahead_constr_global_min_entropy, num_unset, size);
	cfg->lookahead.check_mode.gac.min_entropy
		= g_root_lookahead_gac_local_min_entropy;
	cfg->lookahead.check_mode.gac.max_entropy
		= g_root_lookahead_gac_local_max_entropy;
	cfg->lookahead.check_mode.gac.global_min_entropy
		= calc_effective_global_min_entropy(
			g_root_lookahead_gac_global_min_entropy, num_unset, size);
}
