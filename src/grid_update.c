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
#include "cell_bitmaps.h"
#include "constraint_checking.h"

void	set_grid_val(t_puzzle *puzzle, int cell_idx, int val, int check)
{
	t_node_state	*state;

	state = &puzzle->node_state;
	state->grid.vals[cell_idx] = val;
	state->num_unset--;
	state->last_set_idx = cell_idx;
	update_bitmaps(state, cell_idx, val);
	if (state->num_unset == 0)
		state->is_complete = 1;
	if (check && !state->is_invalid)
		state->is_invalid = !check_constraints(puzzle, cell_idx);
}

int	is_cell_empty(t_puzzle* puzzle, int cell_idx)
{
	return (puzzle->node_state.grid.vals[cell_idx] == 0);
}
