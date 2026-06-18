/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_routing.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 14:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "strategy_routing.h"
#include "prune_initial.h"
#include "prune_root.h"
#include "prune_shallow.h"
#include "prune_medium.h"
#include "prune_deep.h"

static void	update_prune_progress(t_puzzle *puzzle, int prev_num_unset,
		t_prune_prog prev_prog)
{
	puzzle->cur_node->last_prune_nunset = prev_num_unset;
	puzzle->cur_node->last_prune_prog = prev_prog;
	puzzle->cur_node->rows_changed_since_prune = 0;
	puzzle->cur_node->cols_changed_since_prune = 0;
}

void	run_prune_initial_fixpoint(t_puzzle *puzzle)
{
	t_prune_prog	prev_prog;
	int				prev_num_unset;

	if (should_skip_prune_initial(puzzle))
		return ;
	while (1)
	{
		prev_prog = puzzle->cur_node->progress_counter;
		prev_num_unset = puzzle->cur_node->num_unset;
		prune_initial(puzzle);
		update_prune_progress(puzzle, prev_num_unset, prev_prog);
		if (puzzle->cur_node->is_invalid || puzzle->cur_node->is_complete)
			break ;
		if (puzzle->cur_node->progress_counter == prev_prog)
			break ;
	}
}

void	run_prune_root_fixpoint(t_puzzle *puzzle)
{
	t_prune_prog	prev_prog;
	int				prev_num_unset;

	if (should_skip_prune_root(puzzle))
		return ;
	while (1)
	{
		prev_prog = puzzle->cur_node->progress_counter;
		prev_num_unset = puzzle->cur_node->num_unset;
		prune_root(puzzle);
		update_prune_progress(puzzle, prev_num_unset, prev_prog);
		if (puzzle->cur_node->is_invalid || puzzle->cur_node->is_complete)
			break ;
		if (puzzle->cur_node->progress_counter == prev_prog)
			break ;
	}
}

static void	prune_depth_helper(t_puzzle *puzzle)
{
	if (puzzle->cur_node->cur_depth <= 1)
		prune_shallow(puzzle);
	else if (puzzle->cur_node->cur_depth <= 3)
		prune_medium(puzzle);
	else
		prune_deep(puzzle);
}

static int	should_skip_depth(t_puzzle *puzzle)
{
	if (puzzle->cur_node->cur_depth <= 1)
		return (should_skip_prune_shallow(puzzle));
	if (puzzle->cur_node->cur_depth <= 3)
		return (should_skip_prune_medium(puzzle));
	return (should_skip_prune_deep(puzzle));
}

void	run_node_pruning_depth(t_puzzle *puzzle)
{
	t_prune_prog	prev_prog;
	int				prev_num_unset;

	if (should_skip_depth(puzzle))
		return ;
	prev_prog = puzzle->cur_node->progress_counter;
	prev_num_unset = puzzle->cur_node->num_unset;
	prune_depth_helper(puzzle);
	update_prune_progress(puzzle, prev_num_unset, prev_prog);
}
