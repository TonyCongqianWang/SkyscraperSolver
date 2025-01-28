/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_checking.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:51 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 18:18:57 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "constraint_checking.h"

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
		grid_idx = constr->cur_c_pair.grid_indeces[sub_idx];
		insert_val(constr, puzzle->grid_vals[grid_idx]);
		update_constr_bounds(constr);
		sub_idx++;
		if (constr->fwd_lb > constr->cur_c_pair.fwd_val)
			return (0);
		if (constr->fwd_ub < constr->cur_c_pair.fwd_val)
			return (0);
		if (constr->bwd_lb > constr->cur_c_pair.bwd_val)
			return (0);
		if (constr->bwd_ub < constr->cur_c_pair.bwd_val)
			return (0);
	}
	return (1);
}

void	reverse_constr_direction(t_constraint_state *constr)
{
	int		swap;

	constr->is_reverse = !(constr->is_reverse);
	swap = constr->bwd_lb;
	constr->bwd_lb = constr->fwd_lb;
	constr->fwd_lb = swap;
	swap = constr->bwd_ub;
	constr->bwd_ub = constr->fwd_ub;
	constr->fwd_ub = swap;
	swap = constr->cur_c_pair.bwd_val;
	constr->cur_c_pair.bwd_val = constr->cur_c_pair.fwd_val;
	constr->cur_c_pair.fwd_val = swap;
}

void	insert_val(t_constraint_state *constr, int val)
{
	if (val == 0)
		constr->n_unset++;
	else if (val > constr->max_height)
	{
		constr->max_height = val;
		constr->n_seen++;
	}
}

void	update_constr_bounds(t_constraint_state *constr)
{
	int		lhs_ub;
	int		rhs_ub;
	int		new_lb;
	int		size;

	size = constr->cur_c_pair.size;
	new_lb = constr->n_seen;
	if (constr->max_height < size)
		new_lb += 1;
	if (constr->n_unset == 0 && new_lb > constr->fwd_lb)
		constr->fwd_lb = new_lb;
	lhs_ub = constr->n_seen + constr->n_unset;
	rhs_ub = size - constr->max_height;
	if (lhs_ub + rhs_ub < constr->fwd_lb)
		constr->fwd_lb = lhs_ub + rhs_ub;
	if (size + 1 - constr->n_seen < constr->bwd_ub)
		constr->bwd_ub = size + 1 - constr->n_seen;
}
