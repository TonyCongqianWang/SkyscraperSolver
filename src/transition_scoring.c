/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   transition_scoring.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/05/21 02:04:11 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "transition_scoring.h"
#include "grid_availability.h"

void	score_transition_full(t_node_state *state, t_node_transition *next)
{
	double	c_s;
	double	col_s;
	double	row_s;
	int		s1;

	transition_add_num_valids(state, next);
	s1 = state->size + 1;
	c_s = next->num_valids_cell * s1;
	col_s = next->num_valids_col * s1;
	row_s = next->num_valids_row * s1;
	if (next->num_valids_cell <= next->num_valids_col)
		c_s *= s1;
	else
		col_s *= s1;
	if (next->num_valids_cell <= next->num_valids_col)
		c_s *= s1;
	else
		row_s *= s1;
	if (next->num_valids_col <= next->num_valids_row)
		col_s *= s1;
	else
		row_s *= s1;
	next->score = (double)s1 * s1 * s1 * s1 - (c_s + col_s + row_s);
	score_cell_distance(state, next);
}

void	score_cell_distance(t_node_state *state, t_node_transition *next)
{
	int	x;
	int	y;
	int	s;
	int	half;

	s = state->size;
	y = next->cell_idx / s;
	x = next->cell_idx - y * s;
	half = s / 2;
	if (x > half)
		x = s - x;
	if (y > half)
		y = s - y;
	if (x <= y)
		next->score += (s + 1) * (s + 1) - (x * (s + 1) + y);
	else
		next->score += (s + 1) * (s + 1) - (y * (s + 1) + x);
}

void	score_transition_constrs(t_node_state *state, t_node_transition *next)
{
	int	s;

	transition_add_num_valids(state, next);
	s = state->size;
	next->score = (s + 1) * (s + 1);
	if (next->num_valids_col <= next->num_valids_row)
		next->score -= next->num_valids_col * (s + 1) + next->num_valids_row;
	else
		next->score -= next->num_valids_row * (s + 1) + next->num_valids_col;
}

void	transition_add_num_valids(t_node_state *state, t_node_transition *next)
{
	int	idx;
	int	val;

	idx = next->cell_idx;
	val = next->cell_val;
	next->num_valids_col = get_col_num_valids(state, idx, val);
	next->num_valids_row = get_row_num_valids(state, idx, val);
	next->num_valids_cell = get_cell_num_valids(state, idx);
}
