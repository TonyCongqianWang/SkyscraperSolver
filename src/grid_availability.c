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
#include "grid_manipulation.h"
#include "cell_bounds.h"

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

int	get_cell_num_valids(t_node_state *state, int idx)
{
	return (state->grid.num_cell_vals[idx]);
}
