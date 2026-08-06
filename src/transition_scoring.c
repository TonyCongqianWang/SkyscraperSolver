/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   transition_scoring.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:27 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "transition_scoring.h"
#include "grid_availability.h"
#include "params_math.h"
#include "node_selection_score.h"

void	score_transition_full(t_node_state *state, t_node_transition *next)
{
	double	w_cell;
	double	w_line;
	double	*lut;

	transition_add_num_valids(state, next);
	w_cell = get_sel_weight_cell_constr_ratio(state->size);
	w_line = 1.0 - w_cell;
	lut = state->puzzle->selection_lut.values;
	next->score = w_cell * lut[next->num_valids_cell]
		+ w_line * 0.5 * (lut[next->num_valids_col]
			+ lut[next->num_valids_row]);
}

void	transition_add_num_valids(t_node_state *state, t_node_transition *next)
{
	int		idx;
	int		val;

	idx = next->cell_idx;
	val = next->cell_val;
	next->num_valids_col = get_col_num_valids(state, idx, val);
	next->num_valids_row = get_row_num_valids(state, idx, val);
	next->num_valids_cell = get_cell_num_valids(state, idx);
}
