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
#include "cell_bounds.h"
#include "constraint_checking.h"
#include "constraint_selection.h"

void	tighten_grid_cell_bounds(t_puzzle *puzzle)
{
	int			cell_idx;
	int			reiterate;
	int			set_count;

	set_count = puzzle->size * puzzle->size;
	set_count -= puzzle->node_state.total_unset_count;
	reiterate = 1;
	while (reiterate)
	{
		cell_idx = 0;
		reiterate = 0;
		while (cell_idx < puzzle->size * puzzle->size)
		{
			if (puzzle->grid_vals[cell_idx] == 0)
			{
				reiterate |= tighten_single_cell_bounds(puzzle, cell_idx);
			}
			cell_idx++;
		}
		reiterate &= (set_count < puzzle->size);
	}
}

int	check_grid_val_violations(t_puzzle *grid, int cell_idx, int val)
{
	t_node_state	old_state;
	int				success;

	old_state = grid->node_state;
	set_grid_val(grid, cell_idx, val);
	success = check_constraints(grid, cell_idx);
	if (!success)
		register_invalid_val(&old_state, cell_idx, val);
	grid->node_state = old_state;
	unset_grid_val(grid, cell_idx);
	return (!success);
}
#include <stdio.h>
void	register_invalid_val(t_node_state* state, int cell_idx, int val)
{
	short cell_lb, cell_ub;
	set_value_invalid(state, cell_idx, val);
	get_cell_bounds(state, cell_idx, &cell_lb, &cell_ub);
	if (cell_ub < cell_lb)
	{
		state->is_invalid = 1;
	}
}

void	set_grid_val(t_puzzle *grid, int cell_idx, int val)
{
	grid->grid_vals[cell_idx] = val;
	grid->node_state.total_unset_count--;
	update_bitmaps(&grid->node_state, cell_idx, val);
	if (grid->node_state.total_unset_count == 0)
		grid->node_state.is_complete = 1;
}

void	unset_grid_val(t_puzzle *grid, int cell_idx)
{
	grid->grid_vals[cell_idx] = 0;
}
