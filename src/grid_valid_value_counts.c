/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_valid_value_counts.c                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/30 19:48:43 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:17:45 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "grid_valid_value_counts.h"

void	decrement_constr_num_valids(t_node_state *state, int cell_idx, int val)
{
	int		num_valids_col;
	int		num_valids_row;
	int		constr_idx;

	constr_idx = state->puzzle->grid_constr_map[cell_idx][0];
	num_valids_col = --state->num_valid_cells_for_val[constr_idx][val - 1];
	constr_idx = state->puzzle->grid_constr_map[cell_idx][1];
	num_valids_row = --state->num_valid_cells_for_val[constr_idx][val - 1];
	if (num_valids_col == 0 || num_valids_row == 0)
		state->is_invalid = 1;
}

int	get_constr_num_valids(t_node_state *state, int cell_idx, int val)
{
	int		num_valids_col;
	int		num_valids_row;
	int		constr_idx;

	constr_idx = state->puzzle->grid_constr_map[cell_idx][0];
	num_valids_col = state->num_valid_cells_for_val[constr_idx][val - 1];
	constr_idx = state->puzzle->grid_constr_map[cell_idx][1];
	num_valids_row = state->num_valid_cells_for_val[constr_idx][val - 1];
	if (num_valids_col < num_valids_row)
		return (num_valids_col);
	return (num_valids_row);
}

void	decrement_cell_num_valids(t_node_state *state, int idx)
{
	int		num_valids_cell;

	num_valids_cell = --state->num_valid_vals_for_cell[idx];
	if (num_valids_cell == 0)
		state->is_invalid = 1;
}

int	get_cell_num_valids(t_node_state *state, int idx)
{
	return (state->num_valid_vals_for_cell[idx]);
}
