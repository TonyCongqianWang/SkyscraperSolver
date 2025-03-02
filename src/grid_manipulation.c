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
#include "constraint_checking.h"

static void	update_availability(t_node_state *state, int cell_idx, int val);

void	set_grid_val(t_node_state *state, int cell_idx, int val, int check)
{
	state->grid.vals[cell_idx] = val;
	state->num_unset--;
	state->last_set_idx = cell_idx;
	update_availability(state, cell_idx, val);
	if (state->num_unset == 0)
		state->is_complete = 1;
	if (check && !state->is_invalid)
		state->is_invalid = !check_constraints(state->puzzle, cell_idx);
}

void	set_value_invalid(t_node_state *state, int cell_idx, int val)
{
	if (state->is_invalid)
		return ;
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

static void	update_column(t_node_state *state, int cell_idx, int val)
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
		set_value_invalid(state, update_idx, val);
		counter++;
	}
}

static void	update_availability(t_node_state *state, int cell_idx, int val)
{
	int		counter;

	counter = 0;
	while (counter < state->size - 1)
	{
		set_value_invalid(state, cell_idx, ((val + counter) % state->size) + 1);
		counter++;
	}
	update_column(state, cell_idx, val);
	update_row(state, cell_idx, val);
}
