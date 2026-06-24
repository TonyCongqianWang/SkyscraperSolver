/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_shallow.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/20 23:59:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_shallow.h"
#include "pruning_routines.h"

void	prune_shallow(t_puzzle *puzzle)
{
	t_prune_routine_cfg	cfg;
	double				unset_ratio;

	unset_ratio = (double)puzzle->cur_node->num_unset / puzzle->squared_size;
	if (unset_ratio > 0.75)
		get_prune_cfg_heavy(&cfg);
	else if (unset_ratio > 0.4)
		get_prune_cfg_medium(&cfg);
	else if (unset_ratio > 0.3)
		get_prune_cfg_light(&cfg);
	else
		get_prune_cfg_vlight(&cfg);
	run_pruning_routine(puzzle, &cfg);
}

int	should_skip_prune_shallow(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			unset_ratio;
	double			x;
	t_prune_prog	period;

	node = puzzle->cur_node;
	if (node->num_unset == 0)
		return (1);
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	if (unset_ratio < 0.2)
		return (1);
	x = 1 - unset_ratio;
	period = (t_prune_prog)(20 + 10000 * x * x * x * x);
	return (node->progress_counter < node->last_prune_prog + period);
}
