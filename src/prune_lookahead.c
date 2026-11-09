/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_lookahead.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/24 22:52:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_lookahead.h"
#include "pruning_routines.h"
#include "pruning_configs.h"

void	prune_lookahead(t_solver_state *puzzle, t_lookahead_config *config)
{
	t_prune_routine_cfg	cfg;

	init_prune_cfg(&cfg, 0, puzzle->cur_node->tree.lookahead_depth,
		puzzle->size);
	cfg.lookahead = *config;
	cfg.run_lookahead = (config->max_depth > 0);
	run_pruning_routine(puzzle, &cfg, 1);
}
