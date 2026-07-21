/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_manipulation.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "grid_manipulation.h"
#include "grid_availability.h"
#include "grid_update.h"
#include "cell_bounds.h"
#include "grid_availability.h"
#include "check_node_validity.h"
#include "push_dirty_constraints.h"
#include "entropy.h"

static void	update_availability(t_node_state *state, int cell_idx, int val);

void	set_grid_val_internal(t_node_state *state, int cell_idx, int val,
			int check)
{
	if (state->grid.vals[cell_idx] != 0)
	{
		state->is_invalid = 1;
		return ;
	}
	state->grid.vals[cell_idx] = val;
	state->rows_changed_since_prune |= (1 << (cell_idx / state->size));
	state->cols_changed_since_prune |= (1 << (cell_idx % state->size));
	(void)check;
	state->num_unset--;
	state->last_set_idx = cell_idx;
	update_availability(state, cell_idx, val);
	if (state->num_unset == 0)
		state->is_complete = 1;
	if (!state->is_invalid)
		push_dirty_constraints(state, cell_idx);
}

void	set_value_invalid_internal(t_node_state *state, int cell_idx, int val)
{
	int	old_cell_count;

	if (state->is_invalid)
		return ;
	if (state->grid.vals[cell_idx] == val)
		state->is_invalid = 1;
	if (is_valid_value(state, cell_idx, val))
	{
		old_cell_count = state->grid.num_cell_vals[cell_idx];
		state->remaining_entropy -= entropy_delta_cell(old_cell_count);
		state->grid.valid_val_bmps[cell_idx] &= ~(1 << (val - 1));
		update_cell_bounds(state, cell_idx);
		decrement_cell_num_valids(state, cell_idx);
		decrement_constr_num_valids(state, cell_idx, val);
		state->rows_invalid_since_prune |= (1 << (cell_idx / state->size));
		state->cols_invalid_since_prune |= (1 << (cell_idx % state->size));
	}
}

static void	update_column(t_node_state *state, int cell_idx, int val)
{
	int		counter;
	int		update_idx;

	counter = 1;
	while (counter < state->size)
	{
		update_idx = (cell_idx + counter * state->size);
		update_idx %= state->size * state->size;
		set_value_invalid_internal(state, update_idx, val);
		counter++;
	}
}

static void	update_row(t_node_state *state, int cell_idx, int val)
{
	int		counter;
	int		update_idx;

	counter = 1;
	while (counter < state->size)
	{
		update_idx = (cell_idx / state->size) * state->size;
		update_idx += ((cell_idx + counter) % state->size);
		set_value_invalid_internal(state, update_idx, val);
		counter++;
	}
}

static void	update_availability(t_node_state *state, int cell_idx, int val)
{
	int		counter;

	counter = 0;
	while (counter < state->size - 1)
	{
		set_value_invalid_internal(state, cell_idx,
			((val + counter) % state->size) + 1);
		counter++;
	}
	update_column(state, cell_idx, val);
	update_row(state, cell_idx, val);
}
