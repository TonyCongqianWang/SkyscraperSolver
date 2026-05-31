/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_pruning.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_pruning.h"
#include "grid_manipulation.h"
#include "cell_bounds.h"
#include "tree_search.h"
#include "node_selection.h"
#include "constraint_checking.h"
#include "lookahead_dive.h"
#include "solution_storage.h"

static int	skip_pruning(t_puzzle *puzzle);
static int	init_pruning_state(t_puzzle *puzzle, t_node_pruning_state *pruning);
static int	keep_pruning(t_puzzle *puzzle, t_node_pruning_state *pruning);

const double	g_min_unset_r_prune = 0.4;
const double	g_min_unset_r_reit = 0.7;
const int		g_max_p_depth_shallow = 1;
const int		g_depth_threshold_0 = 0;
const int		g_depth_threshold_1 = 3;
const int		g_max_p_depth_deep = 1;
const int		g_prune_period_shallow = 8;
const int		g_prune_extra_period_deep = 15;

void	prune_node(t_puzzle *puzzle)
{
	t_node_pruning_state	pruning;
	t_node_transition		tr;

	pruning = (t_node_pruning_state){0};
	puzzle->cur_node->cur_prune_nunset = puzzle->cur_node->num_unset + 1;
	if (skip_pruning(puzzle))
		return ;
	while (keep_pruning(puzzle, &pruning))
	{
		tr.cell_idx = 0;
		tr.cell_val = 1;
		while (try_get_next_transition(puzzle, &tr))
		{
			if (!do_l_ahead_dive(puzzle, tr, pruning.cur_pruning_depth))
			{
				set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
				pruning.last_iteration_succeeded = 1;
			}
			tr.cell_val++;
		}
	}
	puzzle->cur_node->last_prune_nunset = puzzle->cur_node->cur_prune_nunset;
	puzzle->cur_node->last_prune_prog = puzzle->cur_node->progress_counter;
}

static int	skip_pruning(t_puzzle *puzzle)
{
	unsigned long long	unset_threshold;
	t_node_state		*node;

	node = puzzle->cur_node;
	unset_threshold = node->last_prune_prog;
	unset_threshold += g_prune_period_shallow;
	if (node->cur_depth > g_depth_threshold_0)
		unset_threshold += g_prune_extra_period_deep;
	if (node->cur_depth > g_depth_threshold_1)
		unset_threshold += g_prune_extra_period_deep;
	if (node->progress_counter >= unset_threshold)
		return (1);
	return (0);
}

static int	init_pruning_state(t_puzzle *puzzle, t_node_pruning_state *pruning)
{
	double			unset_quotient;
	t_node_state	*node;

	node = puzzle->cur_node;
	unset_quotient = node->num_unset;
	unset_quotient /= puzzle->squared_size;
	if (unset_quotient < g_min_unset_r_prune)
		return (0);
	if (node->cur_prune_nunset <= node->num_unset)
		return (1);
	else
		node->cur_prune_nunset = node->num_unset;
	pruning->cur_pruning_depth = 0;
	pruning->max_pruning_depth = g_max_p_depth_shallow;
	pruning->can_reiterate = unset_quotient > g_min_unset_r_reit;
	if (node->sub_node_depth == 0
		&& pruning->can_reiterate)
	{
		pruning->cur_pruning_depth = -1;
		pruning->max_pruning_depth = g_max_p_depth_deep;
	}
	pruning->last_iteration_succeeded = 0;
	return (1);
}

static int	keep_pruning(t_puzzle *puzzle, t_node_pruning_state *pruning)
{
	if (!init_pruning_state(puzzle, pruning))
		return (0);
	if (pruning->cur_pruning_depth <= 0)
	{
		pruning->cur_pruning_depth++;
		return (1);
	}
	if (pruning->last_iteration_succeeded && pruning->can_reiterate
		&& pruning->cur_pruning_depth == 1)
	{
		pruning->last_iteration_succeeded = 0;
		return (1);
	}
	else if (pruning->cur_pruning_depth < pruning->max_pruning_depth)
	{
		pruning->last_iteration_succeeded = 0;
		pruning->cur_pruning_depth *= 2;
		return (1);
	}
	return (0);
}
