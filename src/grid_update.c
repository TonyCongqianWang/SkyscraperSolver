/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_update.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "grid_update.h"
#include "cell_bounds.h"
#include "grid_availability.h"
#include "constraint_checking.h"

void	set_grid_val(t_node_state *state, int cell_idx, int val, int check)
{
	state->grid.vals[cell_idx] = val;
	state->num_unset--;
	state->last_set_idx = cell_idx;
	update_bitmaps(state, cell_idx, val);
	if (state->num_unset == 0)
		state->is_complete = 1;
	if (check && !state->is_invalid)
		state->is_invalid = !check_constraints(state->puzzle, cell_idx);
}

int	is_cell_empty(t_node_state *state, int cell_idx)
{
	return (state->grid.vals[cell_idx] == 0);
}

int	is_valid_value(t_node_state *state, int cell_idx, int val)
{
	int		bitmask;
	short	bitmap;

	bitmask = 1 << (val - 1);
	bitmap = state->grid.valid_val_bmps[cell_idx];
	return (bitmask & bitmap);
}

void	set_value_invalid(t_node_state *state, int cell_idx, int val)
{
	if (state->grid.vals[cell_idx] == val)
		state->is_invalid = 1;
	if (is_valid_value(state, cell_idx, val))
	{
		state->grid.valid_val_bmps[cell_idx] &= ~(1 << (val - 1));
		update_cell_bounds(state, cell_idx);
		decrement_cell_num_valids(state, cell_idx);
		decrement_constr_num_valids(state, cell_idx, val);
	}
}

void	update_bitmaps(t_node_state *state, int cell_idx, int val)
{
	int		counter;
	int		update_idx;

	counter = 1;
	while (counter < state->size)
	{
		update_idx = (cell_idx + counter * state->size);
		update_idx %= state->size * state->size;
		set_value_invalid(state, update_idx, val);
		counter++;
	}
	counter = 1;
	while (counter < state->size)
	{
		update_idx = (cell_idx / state->size) * state->size;
		update_idx += ((cell_idx + counter) % state->size);
		set_value_invalid(state, update_idx, val);
		counter++;
	}
}
