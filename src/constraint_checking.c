/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_checking.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:51 by towang            #+#    #+#             */
/*   Updated: 2025/01/29 18:29:46 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "constraint_checking.h"
#include "cell_bitmaps.h"

int	check_active_constr(t_puzzle *puzzle)
{
	int					sub_idx;
	int					grid_idx;
	int					size;
	int					new_val;
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
		new_val = puzzle->grid_vals[grid_idx];
		if(!update_constr_state(puzzle, grid_idx))
			continue;
		if (constr->fwd_lb > constr->cur_c_pair.fwd_val)
			return (0);
		if (constr->fwd_ub < constr->cur_c_pair.fwd_val)
			return (0);
		if (constr->bwd_ub < constr->cur_c_pair.bwd_val)
			return (0);
	}
	return (1);
}

void	set_active_constraint(t_puzzle *puzzle, int constr_idx)
{
	puzzle->constr_state.is_reverse = 0;
	puzzle->constr_state.fwd_lb = 1;
	puzzle->constr_state.fwd_ub = puzzle->size + 1;
	puzzle->constr_state.bwd_ub = puzzle->size + 1;
	puzzle->constr_state.max_height_lb = 1;
	puzzle->constr_state.max_height_ub = 1;
	puzzle->constr_state.cur_c_pair = puzzle->constraint_pairs[constr_idx];
}

void	reverse_constr_direction(t_puzzle *puzzle)
{
	int		swap_bwd;
	int		swap_fwd;

	puzzle->constr_state.is_reverse = !(puzzle->constr_state.is_reverse);
	puzzle->constr_state.fwd_lb = 1;
	puzzle->constr_state.fwd_ub = puzzle->size + 1;
	puzzle->constr_state.bwd_ub = puzzle->size + 1;
	puzzle->constr_state.max_height_lb = 1;
	puzzle->constr_state.max_height_ub = 1;
	swap_fwd = puzzle->constr_state.cur_c_pair.fwd_val;
	swap_bwd = puzzle->constr_state.cur_c_pair.bwd_val;
	puzzle->constr_state.cur_c_pair.fwd_val = swap_bwd;
	puzzle->constr_state.cur_c_pair.bwd_val = swap_fwd;
}

int	update_constr_state(t_puzzle *puzzle, int grid_idx)
{
	int		new_val;
	int		new_val_lb;
	int		new_val_ub;
	t_constraint_state	*constr;

	constr = &puzzle->constr_state;
	new_val = puzzle->grid_vals[grid_idx];
	if (new_val == puzzle->size)
		return (0);
	if (new_val == 0)
	{
		if (constr->max_height_ub == puzzle->size)
			return (1);
		new_val_lb = 1;
		new_val_ub = puzzle->size;
		while (!is_valid_value(&puzzle->node_state, grid_idx, new_val_lb) 
			&& new_val_lb < puzzle->size)
			new_val_lb++;
		while (!is_valid_value(&puzzle->node_state, grid_idx, new_val_ub) 
			&& new_val_ub < puzzle->size)
			new_val_ub--;
		if (new_val_lb > constr->max_height_ub)
		{
			constr->fwd_lb++;
			constr->max_height_lb = new_val_lb;
			constr->max_height_ub = new_val_ub;
		}
		else
		{
			if (new_val_ub > constr->max_height_ub)
				constr->max_height_ub = new_val_ub;
			if (new_val_lb > constr->max_height_lb)
				constr->max_height_lb = new_val_lb;
		}
	}
	else
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
	return (1);
}
