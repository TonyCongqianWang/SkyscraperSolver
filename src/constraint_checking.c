/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_checking.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:51 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 20:47:14 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "constraint_checking.h"
#include "constraint_selection.h"
#include "cell_bitmaps.h"
#include "cell_bounds.h"

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
	short				val_lb;
	short				val_ub;
	t_constraint_state	*constr;

	constr = &puzzle->constr_state;
	new_val = puzzle->grid_vals[grid_idx];
	if (new_val == 0)
	{
		if (constr->max_height_lb == puzzle->size)
			return (1);
		get_cell_bounds(&puzzle->node_state, grid_idx, &val_lb, &val_ub);
		update_constr_bounds_unset(constr, val_lb, val_ub);
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
