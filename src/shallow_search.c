/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   shallow_search.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "shallow_search.h"
#include "grid_update.h"
#include "cell_bounds.h"
#include "puzzle_solver.h"

static int	is_reiterate_allowed(t_node_state *state)
{
	int			set_count;

	set_count = state->size * state->size - state->num_unset;
	return (set_count < state->num_unset / 2 && !state->is_sub_state);
}

static int	check_val_validity(t_puzzle* puzzle, int cell_idx, int val, int depth)
{
	t_node_state	old_state;
	int				is_valid;

	old_state = *(puzzle->cur_node);
	puzzle->cur_node->is_sub_state = 1;
	set_grid_val(puzzle->cur_node, cell_idx, val, 1);
	is_valid = tree_search(puzzle, depth);
	*(puzzle->cur_node) = old_state;
	return (is_valid);
}

static int	tighten_cell_bounds(t_puzzle *puzzle, int idx, int depth)
{
	short			cell_val;
	short			cell_ub;
	int				success;
	t_node_state	*node_state;

	node_state = puzzle->cur_node;
	get_cell_bounds(node_state, idx, &cell_val, &cell_ub);
	success = 0;
	while (cell_val <= cell_ub)
	{
		if (is_valid_value(node_state, idx, cell_val))
		{
			if (!check_val_validity(puzzle, idx, cell_val, depth))
			{
				set_value_invalid(node_state, idx, cell_val);
				success = 1;
			}
		}
		cell_val++;
	}
	return (success);
}

void	reduce_grid_cell_options(t_puzzle* puzzle, int depth)
{
	int			cell_idx;
	int			reiterate;

	reiterate = 1;
	while (reiterate)
	{
		cell_idx = 0;
		reiterate = 0;
		while (cell_idx < puzzle->size * puzzle->size
			&& !puzzle->cur_node->is_invalid)
		{
			if (is_cell_empty(puzzle->cur_node, cell_idx))
				reiterate |= tighten_cell_bounds(puzzle, cell_idx, depth);
			cell_idx++;
		}
		reiterate &= is_reiterate_allowed(puzzle->cur_node);
	}
}

