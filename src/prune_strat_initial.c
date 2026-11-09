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

int	prune_strat_initial(t_solver_state *puzzle)
{
	t_prune_routine_cfg		cfg;

	init_prune_cfg(&cfg, 2, puzzle->cur_node->tree.lookahead_depth,
		puzzle->size);
	cfg.run_gac = 1;
	cfg.run_check_constr = 1;
	return (run_pruning_routine(puzzle, &cfg, 2));
}
