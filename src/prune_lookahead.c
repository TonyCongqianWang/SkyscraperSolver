/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_lookahead.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/20 23:59:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_lookahead.h"
#include "pruning_routines.h"

void	prune_lookahead(t_puzzle *puzzle, t_lookahead_config *config)
{
	t_prune_routine_cfg	cfg;

	get_prune_cfg_light(&cfg);
	cfg.lookahead = *config;
	run_pruning_routine(puzzle, &cfg);
}
