/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_eval.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 10:51:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_eval.h"
#include "node_selection_transition.h"
#include "node_selection_score.h"
#include "grid_availability.h"
#include "cell_bounds.h"
#include "transition_scoring.h"

int	set_next_valid_val(t_puzzle *puzzle, t_node_transition *next)
{
	short	cell_val;
	short	cell_ub;

	get_cell_bounds(puzzle->cur_node, next->cell_idx, &cell_val, &cell_ub);
	if (cell_val < next->cell_val)
		cell_val = next->cell_val;
	while (cell_val <= cell_ub)
	{
		if (is_valid_value(puzzle->cur_node, next->cell_idx, cell_val))
		{
			next->cell_val = cell_val;
			return (1);
		}
		cell_val++;
	}
	return (0);
}

void	sort_node_order(t_node_transition *entries, int count,
			t_selection_criterion criterion)
{
	int					i;
	int					j;
	t_node_transition	key;

	i = 1;
	while (i < count)
	{
		key = entries[i];
		j = i - 1;
		while (j >= 0 && ((criterion == SELECT_MAX
					&& entries[j].score < key.score)
				|| (criterion == SELECT_MIN
					&& entries[j].score > key.score)))
		{
			entries[j + 1] = entries[j];
			j--;
		}
		entries[j + 1] = key;
		i++;
	}
}
