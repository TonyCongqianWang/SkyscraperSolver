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

void	get_prune_cfg_light(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = SELECTIVITY_VALUE_SET;
	cfg->check_constr_min_unset = 0.35;
	cfg->check_constr_max_unset = 0.70;
	cfg->check_constr_global_min_entropy = 513540;
	cfg->run_gac = 0;
	cfg->gac.selectivity = SELECTIVITY_VALUE_SET;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->gac.min_unset = 0.35;
	cfg->gac.max_unset = 0.70;
	cfg->gac.global_min_entropy = 513540;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_VALUE_SET;
	cfg->lookahead.max_depth = 1;
	cfg->lookahead.check_mode = g_check_constr;
}

void	get_prune_cfg_medium(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->check_constr_min_unset = 0.35;
	cfg->check_constr_max_unset = 0.70;
	cfg->check_constr_global_min_entropy = 513540;
	cfg->run_gac = 0;
	cfg->gac.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->gac.min_unset = 0.35;
	cfg->gac.max_unset = 0.70;
	cfg->gac.global_min_entropy = 513540;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->lookahead.max_depth = 1;
	cfg->lookahead.check_mode = g_check_constr;
}

void	get_prune_cfg_heavy(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = SELECTIVITY_NONE;
	cfg->check_constr_min_unset = 0.35;
	cfg->check_constr_max_unset = 0.70;
	cfg->check_constr_global_min_entropy = 513540;
	cfg->run_gac = 0;
	cfg->gac.selectivity = SELECTIVITY_NONE;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->gac.min_unset = 0.35;
	cfg->gac.max_unset = 0.70;
	cfg->gac.global_min_entropy = 513540;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_NONE;
	cfg->lookahead.max_depth = 1;
	cfg->lookahead.check_mode = g_check_constr;
}
