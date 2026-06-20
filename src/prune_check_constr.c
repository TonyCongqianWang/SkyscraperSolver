/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/20 23:59:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_check_constr.h"
#include "pruning_routines.h"

void	prune_check_constr(t_puzzle *puzzle)
{
	t_prune_routine_config	cfg;

	get_prune_cfg_light(&cfg);
	cfg.lookahead.selectivity = SELECTIVITY_NONE;
	cfg.lookahead.max_depth = 0;
	run_pruning_routine(puzzle, &cfg);
}
