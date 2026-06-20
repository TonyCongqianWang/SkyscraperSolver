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
	t_prune_prog			prev_prog;
	t_prune_routine_config	cfg;

	get_prune_cfg_heavy(&cfg);
	cfg.run_check_constr = 1;
	while (1)
	{
		prev_prog = puzzle->cur_node->progress_counter;
		run_pruning_routine(puzzle, &cfg);
		if (puzzle->cur_node->is_invalid || puzzle->cur_node->is_complete)
			break ;
		if (puzzle->cur_node->progress_counter == prev_prog)
			break ;
	}
}
