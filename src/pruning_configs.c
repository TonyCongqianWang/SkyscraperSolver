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

#include "pruning_routines.h"

void	get_prune_cfg_light(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = SELECTIVITY_VALUE_SET;
	cfg->run_gac = 0;
	cfg->gac.selectivity = SELECTIVITY_VALUE_SET;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_VALUE_SET;
	cfg->lookahead.max_depth = 1;
	cfg->lookahead.check_mode = CHECK_CONSTR;
}

void	get_prune_cfg_medium(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->run_gac = 0;
	cfg->gac.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_ANY_CHANGE;
	cfg->lookahead.max_depth = 1;
	cfg->lookahead.check_mode = CHECK_CONSTR;
}

void	get_prune_cfg_heavy(t_prune_routine_cfg *cfg)
{
	cfg->run_check_constr = 0;
	cfg->check_constr_selectivity = SELECTIVITY_NONE;
	cfg->run_gac = 0;
	cfg->gac.selectivity = SELECTIVITY_NONE;
	cfg->gac.max_k = 3;
	cfg->gac.analyse_naked = 1;
	cfg->gac.analyse_hidden = 1;
	cfg->run_lookahead = 1;
	cfg->lookahead.selectivity = SELECTIVITY_NONE;
	cfg->lookahead.max_depth = 1;
	cfg->lookahead.check_mode = CHECK_CONSTR;
}
