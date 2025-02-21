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
#include "grid_valid_value_counts.h"

void	score_transition_full(t_node_state *state, t_node_transition *next)
{
	double	cell_score;
	double	col_score;
	double	row_score;
	int		size;

	transition_add_num_valids(state, next);
	size = state->size;
	cell_score = next->num_valids_cell * (size + 1);
	col_score = next->num_valids_col * (size + 1);
	row_score = next->num_valids_row * (size + 1);
	if (next->num_valids_cell <= next->num_valids_col)
		cell_score *= (size + 1);
	else
		col_score *= (size + 1);
	if (next->num_valids_cell <= next->num_valids_col)
		cell_score *= (size + 1);
	else
		row_score *= (size + 1);
	if (next->num_valids_col <= next->num_valids_row)
		col_score *= (size + 1);
	else
		row_score *= (size + 1);
	next->score = (size + 1) * (size + 1) * (size + 1) * (size + 1);
	next->score -= cell_score + col_score + row_score;
	score_cell_distance(state, next);
}

void	score_cell_distance(t_node_state *state, t_node_transition *next)
{
	double	score_component;
	int		idx;
	int		x_edge_dist;
	int		y_edge_dist;

	idx = next->cell_idx;
	x_edge_dist = idx % state->size;
	if (x_edge_dist > state->size / 2)
		x_edge_dist = state->size - x_edge_dist;
	y_edge_dist = idx / state->size;
	if (y_edge_dist > state->size / 2)
		y_edge_dist = state->size - y_edge_dist;
	score_component = (state->size + 1) * (state->size + 1);
	if (x_edge_dist <= y_edge_dist)
		score_component -= x_edge_dist * (state->size + 1) + y_edge_dist;
	else
		score_component -= y_edge_dist * (state->size + 1) + x_edge_dist;
	next->score += score_component;
}

void	score_transition_constrs(t_node_state *state, t_node_transition *next)
{
	int		size;

	transition_add_num_valids(state, next);
	size = state->size;
	next->score = (size + 1) * (size + 1);
	if (next->num_valids_col <= next->num_valids_row)
		next->score -= next->num_valids_col * (size + 1) + next->num_valids_row;
	else
		next->score -= next->num_valids_row * (size + 1) + next->num_valids_col;
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
