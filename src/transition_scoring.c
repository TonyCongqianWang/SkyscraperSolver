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
	int		ratio;
	double	w_cell;
	double	w_line;
	double	*lut;

	transition_add_num_valids(state, next);
	ratio = get_sel_weight_cell_constr_ratio_fp(state->size);
	w_cell = (double)ratio / 16384.0;
	w_line = (16384.0 - (double)ratio) / 16384.0;
	lut = state->puzzle->selection_lut.values;
	next->score = w_cell * lut[next->num_valids_cell]
		+ w_line * (lut[next->num_valids_col]
			+ lut[next->num_valids_row]);
}

void	score_transition_constrs(t_node_state *state, t_node_transition *next)
{
	double	*lut;

	transition_add_num_valids(state, next);
	lut = state->puzzle->selection_lut.values;
	next->score = lut[next->num_valids_col]
		+ lut[next->num_valids_row];
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
