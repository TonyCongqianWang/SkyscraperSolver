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
#include "params_double.h"

static void	score_progress(t_node_state *state, t_node_transition *next)
{
	next->score = state->lookahead_scores[next->cell_idx][(int)next->cell_val];
}

#ifndef USE_CONSTRS_SCORING
# define USE_CONSTRS_SCORING 0
#endif

void	score_transition_strat(t_node_state *state, t_node_transition *next,
			t_score_family family)
{
	if (family == SCORE_BRANCHING)
	{
		if (USE_CONSTRS_SCORING)
			score_transition_constrs(state, next);
		else
			score_transition_full(state, next);
	}
	else if (family == SCORE_MIN_CANDIDATES)
		next->score = (double)state->grid.num_cell_vals[next->cell_idx];
	else if (family == SCORE_PROGRESS)
		score_progress(state, next);
}

double	calculate_blended_score(t_node_state *node,
			t_node_order *cache, int idx)
{
	double	score_b;
	double	max_e;
	double	curr_e_norm;
	double	e_pos;
	double	e_neg;
	double	score_e;
	double	score_age;
	double	age_factor;

	score_b = cache->meta[idx].cached_br_score;
	if (cache->lookahead_build_entropy < 0)
		return (score_b);
	max_e = (double)node->puzzle->max_entropy;
	curr_e_norm = (double)node->remaining_entropy / max_e;
	e_pos = curr_e_norm;
	if (cache->meta[idx].entropy_pos >= 0)
		e_pos = (double)cache->meta[idx].entropy_pos / max_e;
	e_neg = curr_e_norm;
	if (cache->meta[idx].entropy_neg >= 0)
		e_neg = (double)cache->meta[idx].entropy_neg / max_e;
	score_e = g_lookahead_score_w0 * e_pos + g_lookahead_score_w1 * e_neg
		+ g_lookahead_score_w3 * e_pos * e_neg;
	score_age = (double)(cache->lookahead_build_entropy
			- node->remaining_entropy) / max_e;
	age_factor = g_lookahead_score_w4 - score_age;
	if (age_factor < 0.0)
		age_factor = 0.0;
	return (age_factor * score_e + score_b);
}

void	recalculate_cache_scores(t_node_state *node, t_node_order *cache)
{
	int	i;

	i = 0;
	while (i < cache->count)
	{
		cache->entries[i].score = calculate_blended_score(node, cache, i);
		i++;
	}
}
