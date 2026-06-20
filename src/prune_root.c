/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_root.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/20 23:59:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_root.h"
#include "pruning_routines.h"

void	prune_root(t_puzzle *puzzle)
{
	t_prune_prog			prev_prog;
	t_prune_routine_cfg		cfg;

	get_prune_cfg_heavy(&cfg);
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

int	should_skip_prune_root(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			unset_ratio;
	double			x;
	int				period;

	node = puzzle->cur_node;
	if (node->num_unset == 0)
		return (1);
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	if (unset_ratio < 0.3)
		return (1);
	x = 1 - unset_ratio;
	period = (t_prune_prog)(20 + 25 * x + 30 * x * x + 50 * x * x * x);
	return (node->progress_counter < node->last_prune_prog + period);
}
