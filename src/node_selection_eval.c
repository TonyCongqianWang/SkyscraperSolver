/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_eval.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_eval.h"
#include "node_selection_score.h"
#include "grid_availability.h"
#include "cell_bounds.h"

int	get_cache_index(t_node_state *node)
{
	if (node->is_in_lookahead_select && node->sub_node_depth == 0)
		return (2);
	if (node->sub_node_depth == 0)
		return (0);
	return (1);
}

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

int	is_better(double score, double best_score,
		t_selection_criterion criterion)
{
	if (criterion == SELECT_MAX)
		return (score > best_score);
	return (score < best_score);
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
			if (best->cell_idx == -1 || is_better(cur.score,
					best->score, config->criterion))
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
