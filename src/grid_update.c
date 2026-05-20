/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_update.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/30 19:48:43 by towang            #+#    #+#             */
/*   Updated: 2026/05/21 01:58:34 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "grid_availability.h"
#include "grid_manipulation.h"
#include "cell_bounds.h"

static void	set_valid_val_cell(t_node_state *state, int cell_idx)
{
	short	cell_lb;
	short	cell_ub;

	get_cell_bounds(state, cell_idx, &cell_lb, &cell_ub);
	set_grid_val(state, cell_idx, cell_lb, 1);
}

static void	set_val_in_col(t_node_state *state, int cell_idx, int val)
{
	int	curr_row;
	int	col_start;
	int	row;

	curr_row = cell_idx / state->size;
	col_start = cell_idx - curr_row * state->size;
	row = 0;
	while (row < curr_row)
	{
		if (is_cell_empty(state, col_start + row * state->size)
			&& is_valid_value(state, col_start + row * state->size, val))
			set_grid_val(state, col_start + row * state->size, val, 1);
		row++;
	}
	row = curr_row + 1;
	while (row < state->size)
	{
		if (is_cell_empty(state, col_start + row * state->size)
			&& is_valid_value(state, col_start + row * state->size, val))
			set_grid_val(state, col_start + row * state->size, val, 1);
		row++;
	}
}

static void	set_val_in_row(t_node_state *state, int cell_idx, int val)
{
	int	row_start;
	int	curr_col;
	int	col;

	row_start = (cell_idx / state->size) * state->size;
	curr_col = cell_idx - row_start;
	col = 0;
	while (col < curr_col)
	{
		if (is_cell_empty(state, row_start + col)
			&& is_valid_value(state, row_start + col, val))
			set_grid_val(state, row_start + col, val, 1);
		col++;
	}
	col = curr_col + 1;
	while (col < state->size)
	{
		if (is_cell_empty(state, row_start + col)
			&& is_valid_value(state, row_start + col, val))
			set_grid_val(state, row_start + col, val, 1);
		col++;
	}
}

void	decrement_constr_num_valids(t_node_state *state, int cell_idx, int val)
{
	int	num_valids_col;
	int	num_valids_row;
	int	constr_idx;

	constr_idx = state->puzzle->grid_constr_map[cell_idx][0];
	num_valids_col = --(state->constrs.num_val_positions[constr_idx][val - 1]);
	constr_idx = state->puzzle->grid_constr_map[cell_idx][1];
	num_valids_row = --(state->constrs.num_val_positions[constr_idx][val - 1]);
	if (num_valids_col == 0 || num_valids_row == 0)
	{
		state->is_invalid = 1;
		return ;
	}
	if (num_valids_col == 1 && !state->is_invalid)
		set_val_in_col(state, cell_idx, val);
	if (num_valids_row == 1 && !state->is_invalid)
		set_val_in_row(state, cell_idx, val);
}

void	decrement_cell_num_valids(t_node_state *state, int idx)
{
	int	num_valids_cell;

	num_valids_cell = --(state->grid.num_cell_vals[idx]);
	if (num_valids_cell == 0)
		state->is_invalid = 1;
	else if (num_valids_cell == 1
		&& is_cell_empty(state, idx)
		&& !state->is_invalid)
	{
		set_valid_val_cell(state, idx);
	}
}
