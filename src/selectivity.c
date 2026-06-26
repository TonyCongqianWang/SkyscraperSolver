/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   selectivity.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/26 13:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "selectivity.h"

int	should_exit_selectivity(const t_node_state *node,
		t_selectivity_level selectivity)
{
	if (selectivity == SELECTIVITY_VALUE_SET
		&& node->rows_changed_since_prune == 0
		&& node->cols_changed_since_prune == 0)
		return (1);
	if (selectivity == SELECTIVITY_ANY_CHANGE
		&& node->rows_changed_since_prune == 0
		&& node->cols_changed_since_prune == 0
		&& node->rows_invalid_since_prune == 0
		&& node->cols_invalid_since_prune == 0)
		return (1);
	return (0);
}

int	should_process_row(const t_node_state *state, int r,
		t_selectivity_level selectivity)
{
	if (selectivity == SELECTIVITY_NONE)
		return (1);
	if ((state->rows_changed_since_prune & (1 << r))
		|| (selectivity == SELECTIVITY_ANY_CHANGE
			&& (state->rows_invalid_since_prune & (1 << r))))
		return (1);
	return (0);
}

int	should_process_col(const t_node_state *state, int c,
		t_selectivity_level selectivity)
{
	if (selectivity == SELECTIVITY_NONE)
		return (1);
	if ((state->cols_changed_since_prune & (1 << c))
		|| (selectivity == SELECTIVITY_ANY_CHANGE
			&& (state->cols_invalid_since_prune & (1 << c))))
		return (1);
	return (0);
}
