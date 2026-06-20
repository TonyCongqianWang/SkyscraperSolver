/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_root.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_root.h"
#include "prune_gac.h"
#include "lookahead_dive.h"
#include "node_selection.h"
#include "grid_manipulation.h"

static void	prune_root_step(t_puzzle *puzzle)
{
	t_gac_config		gac_cfg;
	t_node_transition	tr;

	gac_cfg.is_selective = 0;
	gac_cfg.max_k = 3;
	gac_cfg.analyse_naked = 1;
	gac_cfg.analyse_hidden = 1;
	prune_gac(puzzle, &gac_cfg);
	puzzle->cur_node->is_in_lookahead_select = 1;
	puzzle->cur_node->is_selective_lookahead = 0;
	init_node_transition(&tr);
	while (try_get_next_transition(puzzle, &tr))
	{
		if (!do_l_ahead_dive(puzzle, tr, 1))
			set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
	}
	puzzle->cur_node->is_in_lookahead_select = 0;
}

void	prune_root(t_puzzle *puzzle)
{
	t_prune_prog	prev_prog;
	int				prev_num_unset;

	while (1)
	{
		prev_prog = puzzle->cur_node->progress_counter;
		prev_num_unset = puzzle->cur_node->num_unset;
		prune_root_step(puzzle);
		puzzle->cur_node->last_prune_nunset = prev_num_unset;
		puzzle->cur_node->last_prune_prog = prev_prog;
		puzzle->cur_node->rows_changed_since_prune = 0;
		puzzle->cur_node->cols_changed_since_prune = 0;
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
