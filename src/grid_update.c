/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_update.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 20:34:56 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "grid_update.h"
#include "cell_bitmaps.h"
#include "cell_bounds.h"
#include "constraint_checking.h"
#include "constraint_selection.h"

void	tighten_grid_cell_bounds(t_puzzle *puzzle)
{
	int			loop_idx;
	int			cell_idx;
	int			continue_loop;

	loop_idx = 0;
	continue_loop = puzzle->node_state.total_unset_count < puzzle->size;
	while (loop_idx < puzzle->size * puzzle->size || continue_loop)
	{
		cell_idx = loop_idx % (puzzle->size * puzzle->size);
		if (puzzle->grid_vals[cell_idx] == 0)
		{
			continue_loop &= tighten_single_cell_bounds(puzzle, cell_idx);
		}
		loop_idx++;
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
		set_value_invalid(&old_state, cell_idx, val);
	grid->node_state = old_state;
	unset_grid_val(grid, cell_idx);
	return (!success);
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

int	check_constraints(t_puzzle *puzzle, int insert_idx)
{
	int					rel_idx;
	int					abs_idx;

	rel_idx = 0;
	while (rel_idx < 2)
	{
		abs_idx = puzzle->grid_constr_map[insert_idx][rel_idx];
		set_active_constraint(puzzle, abs_idx);
		if (!check_active_constr(puzzle))
			return (0);
		reverse_constr_direction(puzzle);
		if (!check_active_constr(puzzle))
			return (0);
		rel_idx++;
	}
	return (1);
}
