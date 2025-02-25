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
#include "grid_update.h"
#include "cell_bounds.h"
#include "puzzle_solver.h"

static int	init_pruning_state(t_puzzle *puzzle);
static int	keep_pruning(t_node_pruning_state *state);
static int	check_validity(t_puzzle *puzzle, t_node_transition next);
static int	set_valid_val(t_puzzle *puzzle, t_node_transition *next);
static int	get_valid_transition(t_puzzle *puzzle, t_node_transition *next);

void	prune_node(t_puzzle *puzzle)
{
	t_node_transition	tr;

	if (!init_pruning_state(puzzle))
		return ;
	while (keep_pruning(&puzzle->pruning))
	{
		tr.cell_idx = 0;
		tr.cell_val = 1;
		while (get_valid_transition(puzzle, &tr))
		{
			if (!check_validity(puzzle, tr))
			{
				set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
				puzzle->pruning.last_iteration_succeeded = 1;
			}
			tr.cell_val++;
		}
	}
}

static int	init_pruning_state(t_puzzle *puzzle)
{
	const double	max_set_unset_quotient = 0.5;
	t_node_state	*state;
	int				set_count;
	int				reiterate;

	state = puzzle->cur_node;
	puzzle->pruning.max_pruning_depth = 1;
	set_count = puzzle->size * puzzle->size - state->num_unset;
	reiterate = (set_count < max_set_unset_quotient * state->num_unset);
	puzzle->pruning.can_reiterate = reiterate;
	puzzle->pruning.cur_pruning_depth = 0;
	puzzle->pruning.last_iteration_succeeded = 0;
	return (1);
}

static int	keep_pruning(t_node_pruning_state *state)
{
	if (state->last_iteration_succeeded
		&& state->can_reiterate)
	{
		state->last_iteration_succeeded = 0;
		return (1);
	}
	else if (state->cur_pruning_depth < state->max_pruning_depth)
	{
		state->last_iteration_succeeded = 0;
		state->cur_pruning_depth++;
		return (1);
	}
	return (0);
}

static int	check_validity(t_puzzle *puzzle, t_node_transition next)
{
	t_node_state	old_state;
	int				is_valid;

	old_state = *(puzzle->cur_node);
	puzzle->cur_node->max_depth = puzzle->pruning.cur_pruning_depth;
	puzzle->cur_node->cur_depth++;
	puzzle->cur_node->sub_node_depth++;
	set_grid_val(puzzle->cur_node, next.cell_idx, next.cell_val, 1);
	is_valid = tree_search(puzzle);
	*(puzzle->cur_node) = old_state;
	return (is_valid);
}

static int	set_valid_val(t_puzzle *puzzle, t_node_transition *next)
{
	short			cell_val;
	short			cell_ub;

	get_cell_bounds(puzzle->cur_node, next->cell_idx, &cell_val, &cell_ub);
	if (cell_val < next->cell_val)
		cell_val = next->cell_val;
	while (cell_val <= cell_ub)
	{
		if (is_valid_value(puzzle->cur_node, next->cell_idx, cell_val))
		{
			next->cell_val = cell_val;
			return (1);
		}
		cell_val++;
	}
	return (0);
}

static int	get_valid_transition(t_puzzle *puzzle, t_node_transition *next)
{
	int		cell_idx;

	if (puzzle->cur_node->is_complete || puzzle->cur_node->is_invalid)
		return (0);
	cell_idx = next->cell_idx;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		if (is_cell_empty(puzzle->cur_node, cell_idx))
		{
			next->cell_idx = cell_idx;
			if (set_valid_val(puzzle, next))
				return (1);
		}
		cell_idx++;
		next->cell_val = 1;
	}
	return (0);
}
