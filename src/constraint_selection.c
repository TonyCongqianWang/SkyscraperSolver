/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_selection.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:51 by towang            #+#    #+#             */
/*   Updated: 2025/01/29 22:43:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "constraint_selection.h"

void	set_active_constraint(t_puzzle *puzzle, int constr_idx)
{
	reset_constraint_bounds(puzzle);
	puzzle->constr_state.is_reverse = 0;
	puzzle->constr_state.cur_c_pair = puzzle->constraint_pairs[constr_idx];
}

void	reverse_constr_direction(t_puzzle *puzzle)
{
	int		swap_bwd;
	int		swap_fwd;

	reset_constraint_bounds(puzzle);
	puzzle->constr_state.is_reverse = !(puzzle->constr_state.is_reverse);
	swap_fwd = puzzle->constr_state.cur_c_pair.fwd_val;
	swap_bwd = puzzle->constr_state.cur_c_pair.bwd_val;
	puzzle->constr_state.cur_c_pair.fwd_val = swap_bwd;
	puzzle->constr_state.cur_c_pair.bwd_val = swap_fwd;
}

void	reset_constraint_bounds(t_puzzle *puzzle)
{
	puzzle->constr_state.fwd_lb = 1;
	puzzle->constr_state.fwd_ub = puzzle->size;
	puzzle->constr_state.lhs_ub = 0;
	puzzle->constr_state.bwd_ub = puzzle->size + 1;
	puzzle->constr_state.max_height_lb = 0;
	puzzle->constr_state.max_height_ub = 0;
}
