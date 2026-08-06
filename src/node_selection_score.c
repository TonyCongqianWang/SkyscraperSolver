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
#include "params_double.h"
#include "params_math.h"

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

static void	get_normalized_entropies(t_node_state *node,
				t_transition_meta *meta, double *e_pos, double *e_neg)
{
	double	max_e;

	max_e = (double)node->puzzle->max_entropy;
	*e_pos = (double)node->remaining_entropy / max_e;
	if (meta->entropy_pos >= 0)
		*e_pos = (double)meta->entropy_pos / max_e;
	*e_neg = (double)node->remaining_entropy / max_e;
	if (meta->entropy_neg >= 0)
		*e_neg = (double)meta->entropy_neg / max_e;
}

double	calculate_blended_score(t_node_state *node,
			t_node_order *cache, int idx)
{
	double	s0;
	double	s1;
	double	e_pos;
	double	e_neg;
	double	age_lim;

	if (cache->lookahead_build_entropy < 0)
		return (cache->meta[idx].cached_br_score);
	get_clamped_splits(node, &s0, &s1);
	get_normalized_entropies(node, &cache->meta[idx], &e_pos, &e_neg);
	age_lim = get_lookahead_score_age_limit_ratio(node->puzzle->size)
		* node->puzzle->max_entropy;
	if (cache->lookahead_build_entropy - node->remaining_entropy >= age_lim
		|| age_lim <= 0.0)
		return (cache->meta[idx].cached_br_score);
	age_lim = (age_lim - (cache->lookahead_build_entropy
				- node->remaining_entropy)) / age_lim;
	return (age_lim * get_lookahead_entropy_weight(node->puzzle->size)
		* (1.0 - (s0 * e_pos + (1.0 - s1) * e_neg + (s1 - s0) * e_pos
				* e_neg)) + cache->meta[idx].cached_br_score);
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
