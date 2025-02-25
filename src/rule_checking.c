/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rule_checking.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:36 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 20:55:43 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "rule_checking.h"

static int	is_rule_violated(t_puzzle *puzzle, int constr_idx, int reverse);

int	check_rule_violations(t_puzzle *puzzle)
{
	int		constr_idx;

	constr_idx = 0;
	while (constr_idx < 2 * puzzle->size)
	{
		if (is_rule_violated(puzzle, constr_idx, 0))
			return (1);
		if (is_rule_violated(puzzle, constr_idx, 1))
			return (1);
		constr_idx++;
	}
	return (0);
}

static void	init_state(t_constr_check_state *state, t_constraint_pair constr)
{
	state->constr_pair = constr;
	state->seen_bmp = 0;
	state->cur_max_height = 0;
	state->cur_num_visible = 0;
}

static int	try_add_value(t_constr_check_state *state, int val)
{
	int		mask;

	mask = 1 << val;
	if (val != 0 && mask & state->seen_bmp)
		return (0);
	state->seen_bmp |= mask;
	if (val > state->cur_max_height)
	{
		state->cur_max_height = val;
		state->cur_num_visible++;
	}
	return (1);
}

static int	is_rule_violated(t_puzzle *puzzle, int constr_idx, int reverse)
{
	t_constr_check_state	state;
	int						idx;
	int						grid_idx;
	int						grid_val;
	int						target_val;

	init_state(&state, puzzle->constraint_pairs[constr_idx]);
	idx = 0;
	while (idx < puzzle->size)
	{
		if (!reverse)
			grid_idx = state.constr_pair.grid_indeces[idx];
		else
			grid_idx = state.constr_pair.grid_indeces[puzzle->size - idx - 1];
		grid_val = puzzle->cur_node->grid.vals[grid_idx];
		if (!try_add_value(&state, grid_val))
			return (1);
		idx++;
	}
	if (!reverse)
		target_val = state.constr_pair.fwd_val;
	else
		target_val = state.constr_pair.bwd_val;
	return (!(state.seen_bmp & 1) && (state.cur_num_visible != target_val)
		&& target_val != 0);
}
