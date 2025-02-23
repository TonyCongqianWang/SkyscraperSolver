/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_availability.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/30 19:48:43 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:17:45 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "grid_availability.h"
#include "grid_update.h"
#include "cell_bounds.h"

void	decrement_constr_num_valids(t_node_state *state, int cell_idx, int val)
{
	int		num_valids_col;
	int		num_valids_row;
	int		constr_idx;

	constr_idx = state->puzzle->grid_constr_map[cell_idx][0];
	num_valids_col = --(state->constrs.num_val_positions[constr_idx][val - 1]);
	constr_idx = state->puzzle->grid_constr_map[cell_idx][1];
	num_valids_row = --(state->constrs.num_val_positions[constr_idx][val - 1]);
	if (num_valids_col == 0 || num_valids_row == 0)
		state->is_invalid = 1;
}

int	get_col_num_valids(t_node_state *state, int cell_idx, int val)
{
	int		constr_idx;

	constr_idx = state->puzzle->grid_constr_map[cell_idx][0];
	return (state->constrs.num_val_positions[constr_idx][val - 1]);
}

int	get_row_num_valids(t_node_state *state, int cell_idx, int val)
{
	int		constr_idx;

	constr_idx = state->puzzle->grid_constr_map[cell_idx][1];
	return (state->constrs.num_val_positions[constr_idx][val - 1]);
}

void	decrement_cell_num_valids(t_node_state *state, int idx)
{
	int		num_valids_cell;
	short	cell_lb;
	short	cell_ub;

	num_valids_cell = --(state->grid.num_cell_vals[idx]);
	if (num_valids_cell == 0)
		state->is_invalid = 1;
	else if (num_valids_cell == 1
		&& is_cell_empty(state, idx)
		&& !state->is_invalid)
	{
		get_cell_bounds(state, idx, &cell_lb, &cell_ub);
		set_grid_val(state, idx, cell_lb, 1);
	}
}

int	get_cell_num_valids(t_node_state *state, int idx)
{
	return (state->grid.num_cell_vals[idx]);
}
