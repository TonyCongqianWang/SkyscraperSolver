/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_api.c                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/19 19:35:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 19:15:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"
#include "node_selection_eval.h"
#include "grid_availability.h"

#ifndef USE_CONSTRS_SCORING
# define USE_CONSTRS_SCORING 0
#endif

static double	get_best_possible_score(t_node_state *state,
					t_node_select_config *config)
{
	int	size;

	size = state->size;
	if (config->score_family == SCORE_BRANCHING)
	{
		if (USE_CONSTRS_SCORING)
			return ((double)((size + 1) * (size + 1) - (size + 1) - 1));
		else
			return ((double)((size + 1) * (size + 1) * (size + 1) * (size + 1)
				- (size + 1) * (size + 1) * (size + 1) - (size + 1)));
	}
	else if (config->score_family == SCORE_MIN_CANDIDATES)
		return (1.0);
	return (-1e9);
}

static int	is_best_score(double score, double best_possible,
				t_selection_criterion criterion)
{
	if (criterion == SELECT_MAX && score >= best_possible)
		return (1);
	if (criterion == SELECT_MIN && score <= best_possible)
		return (1);
	return (0);
}

static int	is_better_score(double cand_score, double best_score,
				t_selection_criterion criterion)
{
	if (criterion == SELECT_MAX && cand_score > best_score)
		return (1);
	if (criterion == SELECT_MIN && cand_score < best_score)
		return (1);
	return (0);
}

static int	check_and_rescore_best(t_puzzle *puzzle,
				t_best_search_ctx *ctx, int i)
{
	t_node_order		*cache;
	t_node_transition	cand;

	cache = puzzle->cur_node->order_cache;
	if (is_best_score(cache->entries[i].score, ctx->best_possible,
			ctx->config->criterion))
	{
		if (try_cached_entry(puzzle, ctx->next, cache, i))
			return (1);
	}
	set_best_val_strat(puzzle, cache->entries[i].cell_idx, &cand, ctx->config);
	if (cand.cell_idx != -1)
	{
		if (is_best_score(cand.score, ctx->best_possible,
				ctx->config->criterion))
		{
			*ctx->next = cand;
			return (1);
		}
		if (ctx->best->cell_idx == -1
			|| is_better_score(cand.score, ctx->best->score,
				ctx->config->criterion))
			*ctx->best = cand;
	}
	return (0);
}

int	get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
		t_node_select_config *config)
{
	t_node_state		*node;
	t_best_search_ctx	ctx;
	t_node_transition	best;
	int					i;

	node = puzzle->cur_node;
	ctx = (t_best_search_ctx){next, &best, config,
		get_best_possible_score(node, config)};
	best.cell_idx = -1;
	i = node->lowest_empty_idx;
	while (i < node->order_cache->count)
	{
		if (is_cell_empty(node, node->order_cache->entries[i].cell_idx)
			&& check_sel_filter(node, node->order_cache->entries[i].cell_idx,
				puzzle->size, config->selectivity)
			&& check_and_rescore_best(puzzle, &ctx, i))
			return (1);
		i++;
	}
	if (best.cell_idx == -1)
		return (0);
	*next = best;
	return (1);
}
