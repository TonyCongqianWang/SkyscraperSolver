/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_score_strat.c                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_score.h"
#include "transition_scoring.h"

void	score_transition_strat(t_node_state *state, t_node_transition *next)
{
	score_transition_full(state, next);
	if (state->solver->selection_lut.min_score == 0.0)
		next->score = 0.0;
	else
		next->score = 1.0 - next->score
			/ state->solver->selection_lut.min_score;
}
