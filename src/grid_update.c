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
		while (cell_idx < puzzle->size * puzzle->size
			&& !puzzle->node_state.is_invalid)
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

int	check_grid_val_violations(t_puzzle *puzzle, int cell_idx, int val)
{
	t_node_state	old_state;
	int				success;

	old_state = puzzle->node_state;
	set_grid_val(puzzle, cell_idx, val);
	success = check_constraints(puzzle, cell_idx);
	puzzle->node_state = old_state;
	unset_grid_val(puzzle, cell_idx);
	return (!success);
}

void	set_grid_val(t_puzzle *puzzle, int cell_idx, int val)
{
	puzzle->grid_vals[cell_idx] = val;
	puzzle->node_state.total_unset_count--;
	puzzle->node_state.last_set_idx = cell_idx;
	update_bitmaps(&puzzle->node_state, cell_idx, val);
	if (puzzle->node_state.total_unset_count == 0)
		puzzle->node_state.is_complete = 1;
}

void	unset_grid_val(t_puzzle *puzzle, int cell_idx)
{
	puzzle->grid_vals[cell_idx] = 0;
}
