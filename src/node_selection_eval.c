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
#include "node_selection_score.h"
#include "grid_availability.h"
#include "cell_bounds.h"

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

void	set_best_val_strat(t_puzzle *puzzle, int idx,
			t_node_transition *best, t_node_select_config *config)
{
	t_node_transition	cur;
	int					val;

	best->cell_idx = -1;
	cur.cell_idx = idx;
	val = 1;
	while (val <= puzzle->size)
	{
		if (is_valid_value(puzzle->cur_node, idx, val))
		{
			cur.cell_val = val;
			score_transition_strat(puzzle->cur_node, &cur,
				config->score_family);
			if (best->cell_idx == -1
				|| (config->criterion == SELECT_MAX && cur.score > best->score)
				|| (config->criterion == SELECT_MIN && cur.score < best->score))
				*best = cur;
		}
		val++;
	}
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

int	scan_best_live(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_transition	candidate;
	int					cell_idx;

	next->cell_idx = -1;
	cell_idx = 0;
	while (cell_idx < puzzle->squared_size)
	{
		if (is_cell_empty(puzzle->cur_node, cell_idx))
		{
			set_best_val_strat(puzzle, cell_idx, &candidate, config);
			if (candidate.cell_idx != -1)
			{
				if (next->cell_idx == -1
					|| (config->criterion == SELECT_MAX
						&& candidate.score > next->score)
					|| (config->criterion == SELECT_MIN
						&& candidate.score < next->score))
					*next = candidate;
			}
		}
		cell_idx++;
	}
	return (next->cell_idx != -1);
}
