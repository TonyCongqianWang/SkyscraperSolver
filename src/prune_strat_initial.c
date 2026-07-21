/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_initial.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_initial.h"
#include "pruning_routines.h"
#include "pruning_configs.h"

int	prune_strat_initial(t_puzzle *puzzle)
{
	t_prune_routine_cfg		cfg;

	get_prune_cfg_heavy(&cfg);
	cfg.run_gac = 1;
	cfg.run_check_constr = 1;
	cfg.check_constr_selectivity = SELECTIVITY_NONE;
	cfg.lookahead.selectivity = SELECTIVITY_NONE;
	cfg.lookahead.check_mode = g_check_constr;
	return (run_pruning_routine(puzzle, &cfg, 2));
}
