/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_checking.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:51 by towang            #+#    #+#             */
/*   Updated: 2025/01/29 19:11:26 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "constraint_checking.h"
#include "constraint_selection.h"
#include "cell_bitmaps.h"

int	check_active_constr(t_puzzle *puzzle)
{
	int					sub_idx;
	int					grid_idx;
	int					size;
	t_constraint_state	*constr;

	constr = &puzzle->constr_state;
	size = constr->cur_c_pair.size;
	sub_idx = 0;
	while (sub_idx < size)
	{
		if (constr->is_reverse)
			grid_idx = constr->cur_c_pair.grid_indeces[size - sub_idx - 1];
		else
			grid_idx = constr->cur_c_pair.grid_indeces[sub_idx];
		sub_idx++;
		if (!update_constr_state(puzzle, grid_idx))
			return (1);
		if (constr->fwd_lb > constr->cur_c_pair.fwd_val)
			return (0);
		if (constr->fwd_ub < constr->cur_c_pair.fwd_val)
			return (0);
		if (constr->bwd_ub < constr->cur_c_pair.bwd_val)
			return (0);
	}
	return (1);
}

int	update_constr_state(t_puzzle *puzzle, int grid_idx)
{
	int					new_val;
	int					new_val_lb;
	int					new_val_ub;
	t_constraint_state	*constr;

	constr = &puzzle->constr_state;
	new_val = puzzle->grid_vals[grid_idx];
	if (new_val == puzzle->size)
		return (0);
	if (new_val == 0)
	{
		if (constr->max_height_ub == puzzle->size)
			return (1);
		find_cell_bounds(puzzle, grid_idx, &new_val_lb, &new_val_ub);
		update_constr_bounds_unset(constr, new_val_lb, new_val_ub);
	}
	else
	{
		update_constr_bounds_new_val(constr, new_val);
	}
	return (1);
}

void	update_constr_bounds_new_val(t_constraint_state	*constr, int new_val)
{
	if (new_val > constr->max_height_lb)
	{
		constr->max_height_lb = new_val;
		if (new_val > constr->max_height_ub)
		{
			constr->max_height_ub = new_val;
			constr->bwd_ub--;
			constr->fwd_ub -= new_val - constr->max_height_ub - 1;
			constr->fwd_lb++;
		}
	}
	else
		constr->fwd_ub--;
}

void	find_cell_bounds(t_puzzle *puzzle, int cell_idx, int *lb, int *ub)
{
	*lb = 1;
	while (!is_valid_value(&puzzle->node_state, cell_idx, *lb)
		&& *lb < puzzle->size)
	{
		(*lb)++;
	}
	*ub = puzzle->size;
	while (!is_valid_value(&puzzle->node_state, cell_idx, *ub)
		&& *ub > 0)
	{
		(*ub)--;
	}
}

void	update_constr_bounds_unset(t_constraint_state *constr, int lb, int ub)
{
	if (lb > constr->max_height_ub)
	{
		constr->fwd_lb++;
		constr->max_height_lb = lb;
		constr->max_height_ub = ub;
	}
	else
	{
		if (ub > constr->max_height_ub)
			constr->max_height_ub = ub;
		if (lb > constr->max_height_lb)
			constr->max_height_lb = lb;
	}
}
