/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_checking.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:51 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 17:59:02 by towang           ###   ########.fr       */
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
	size = constr->size;
	sub_idx = 0;
	while (sub_idx < size && constr->max_height_lb < size)
	{
		if (constr->is_reverse)
			grid_idx = constr->cur_c_pair.grid_indeces[size - sub_idx - 1];
		else
			grid_idx = constr->cur_c_pair.grid_indeces[sub_idx];
		sub_idx++;
		update_constr_state(puzzle, grid_idx);
		if (constr->fwd_lb > constr->cur_c_pair.fwd_val
			|| constr->fwd_ub < constr->cur_c_pair.fwd_val
			|| constr->bwd_ub < constr->cur_c_pair.bwd_val)
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
	if (new_val == 0)
	{
		if (constr->max_height_lb == puzzle->size)
			return (1);
		new_val_lb = 1;
		new_val_ub = puzzle->size;
		find_cell_bounds(puzzle, grid_idx, &new_val_lb, &new_val_ub);
		update_constr_bounds_unset(constr, new_val_lb, new_val_ub);
		return (1);
	}
	else
	{
		return (update_constr_bounds_new_val(constr, new_val));
	}
}

void	update_constr_bounds_unset(t_constraint_state *constr, int lb, int ub)
{
	if (ub > constr->max_height_lb)
	{
		constr->lhs_ub++;
		if (lb > constr->max_height_ub)
		{
			constr->max_height_lb = lb;
			constr->max_height_ub = ub;
			if (ub != constr->size)
				constr->fwd_lb++;
		}
		else
		{
			if (ub > constr->max_height_ub)
				constr->max_height_ub = ub;
			if (lb > constr->max_height_lb)
				constr->max_height_lb = lb;
		}
	}
}

int	update_constr_bounds_new_val(t_constraint_state	*constr, int new_val)
{
	if (new_val == constr->size)
	{
		constr->max_height_lb = constr->size;
		constr->fwd_ub = constr->lhs_ub + 1;
		return (0);
	}
	if (new_val > constr->max_height_lb)
	{
		constr->lhs_ub++;
		constr->max_height_lb = new_val;
		if (new_val > constr->max_height_bwd)
		{
			constr->bwd_ub--;
			constr->max_height_bwd = new_val;
			if (new_val > constr->max_height_ub)
			{
				constr->fwd_lb++;
				constr->max_height_ub = new_val;
			}
		}
	}
	constr->fwd_ub = constr->lhs_ub;
	constr->fwd_ub += constr->size - constr->max_height_lb;
	return (1);
}

void	find_cell_bounds(t_puzzle *puzzle, int cell_idx, int *lb, int *ub)
{
	return;
	while (*lb < puzzle->size
		&& !is_valid_value(&puzzle->node_state, cell_idx, *lb))
	{
		(*lb)++;
	}
	while (*ub > 1
		&& !is_valid_value(&puzzle->node_state, cell_idx, *ub))
	{
		(*ub)--;
	}
}
