/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_score.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_score.h"
#include "transition_scoring.h"

static void	score_progress(t_node_state *state, t_node_transition *next)
{
	next->score = state->lookahead_scores[next->cell_idx][(int)next->cell_val];
}

void	score_transition_strat(t_node_state *state, t_node_transition *next,
			t_score_family family)
{
	if (family == SCORE_BRANCHING)
		score_transition_full(state, next);
	else if (family == SCORE_MIN_CANDIDATES)
		next->score = (double)state->grid.num_cell_vals[next->cell_idx];
	else if (family == SCORE_PROGRESS)
		score_progress(state, next);
}
