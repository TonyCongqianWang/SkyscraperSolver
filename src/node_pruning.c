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

static int	is_reiterate_allowed(t_node_state *state)
{
	int		set_count;

	set_count = state->size * state->size - state->num_unset;
	return (set_count < state->num_unset / 2 && !state->is_sub_state);
}

static int	check_validity(t_puzzle *puzzle, t_node_transition next, int depth)
{
	t_node_state	old_state;
	int				is_valid;

	old_state = *(puzzle->cur_node);
	puzzle->cur_node->is_sub_state = 1;
	set_grid_val(puzzle->cur_node, next.cell_idx, next.cell_val, 1);
	is_valid = tree_search(puzzle, depth);
	*(puzzle->cur_node) = old_state;
	return (is_valid);
}

static int	set_valid_val(t_puzzle *puzzle, t_node_transition* next)
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

static int	get_valid_transition(t_puzzle *puzzle, t_node_transition* next)
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

void	prune_node(t_puzzle *puzzle, int depth)
{
	int					reiterate;
	t_node_transition	tr;

	reiterate = 1;
	while (reiterate)
	{
		tr.cell_idx = 0;
		tr.cell_val = 1;
		reiterate = 0;
		while (get_valid_transition(puzzle, &tr))
		{
			if (!check_validity(puzzle, tr, depth))
			{
				set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
				reiterate = 1;
			}
			tr.cell_val++;
		}
		reiterate &= is_reiterate_allowed(puzzle->cur_node);
	}
}
