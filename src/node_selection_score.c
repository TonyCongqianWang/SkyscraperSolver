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

static void	get_clamped_splits(t_node_state *node, double *s0, double *s1)
{
	*s0 = get_lookahead_score_weight_split0(node->puzzle->size);
	*s1 = get_lookahead_score_weight_split1(node->puzzle->size);
	if (*s0 < 0.0)
		*s0 = 0.0;
	if (*s1 < *s0)
		*s1 = *s0;
	if (*s1 > 1.0)
		*s1 = 1.0;
}

double	calculate_blended_score(t_node_state *node,
			t_node_order *cache, int idx)
{
	double	s0;
	double	s1;
	double	e_pos;
	double	e_neg;
	double	max_e;
	double	age;
	double	age_factor;

	if (cache->lookahead_build_entropy < 0)
		return (cache->meta[idx].cached_br_score);
	get_clamped_splits(node, &s0, &s1);
	max_e = (double)node->puzzle->max_entropy;
	e_pos = (double)node->remaining_entropy / max_e;
	if (cache->meta[idx].entropy_pos >= 0)
		e_pos = (double)cache->meta[idx].entropy_pos / max_e;
	e_neg = (double)node->remaining_entropy / max_e;
	if (cache->meta[idx].entropy_neg >= 0)
		e_neg = (double)cache->meta[idx].entropy_neg / max_e;
	age = (double)(cache->lookahead_build_entropy - node->remaining_entropy);
	age_factor = 0.0;
	if (age < g_lookahead_score_age_limit && g_lookahead_score_age_limit > 0.0)
		age_factor = (g_lookahead_score_age_limit - age)
			/ g_lookahead_score_age_limit;
	return (age_factor * -(s0 * e_pos + (1.0 - s1) * e_neg
			+ (s1 - s0) * e_pos * e_neg) + cache->meta[idx].cached_br_score);
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
