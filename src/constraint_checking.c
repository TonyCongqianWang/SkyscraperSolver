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
#include "constraint_update.h"

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
		sub_idx++;
		if (constr->is_reverse)
			grid_idx = constr->cur_c_pair.grid_indeces[size - sub_idx];
		else
			grid_idx = constr->cur_c_pair.grid_indeces[sub_idx - 1];
		update_constr_state(puzzle, grid_idx);
		if (sub_idx > constr->max_height_lb)
			constr->max_height_lb = sub_idx;
		if (check_constr_state_violations(&puzzle->constr_state))
			return (0);
	}
	return (1);
}

int	check_constr_state_violations(t_constraint_state *constr)
{
	int		fwd_ub;

	fwd_ub = constr->lhs_ub + constr->size - constr->max_height_lb;
	return (constr->fwd_lb > constr->cur_c_pair.fwd_val
		|| fwd_ub < constr->cur_c_pair.fwd_val
		|| constr->bwd_ub < constr->cur_c_pair.bwd_val);
}
