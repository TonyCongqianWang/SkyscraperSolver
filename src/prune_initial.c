/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_initial.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/20 23:59:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_initial.h"
#include "pruning_routines.h"

void	prune_initial(t_puzzle *puzzle)
{
	t_prune_routine_cfg		cfg;

	get_prune_cfg_heavy(&cfg);
	cfg.run_check_constr = 1;
	run_pruning_routine(puzzle, &cfg);
}
