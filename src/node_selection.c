/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 11:03:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection.h"
#include "node_selection_transition.h"
#include "transition_scoring.h"
#include "grid_availability.h"
#include "strategy_routing.h"
#include "node_selection_cache.h"
#include "node_selection_eval.h"

#ifdef LOOKAHEAD_CRITERION

static const t_selection_criterion	g_lh_criterion = LOOKAHEAD_CRITERION;
static const int					g_lh_criterion_defined = 1;

#else

static const t_selection_criterion	g_lh_criterion = SELECT_MAX;
static const int					g_lh_criterion_defined = 0;

#endif

static void	init_select_config(t_solver_state *puzzle,
				t_node_select_config *config)
{
	t_node_state	*node;

	node = puzzle->cur_node;
	select_node_select_config(puzzle, config);
	if (node->lookahead_ctx)
	{
		config->selectivity = node->lookahead_ctx->selectivity;
		if (g_lh_criterion_defined)
			config->criterion = g_lh_criterion;
	}
}

int	try_select_transition(t_solver_state *puzzle, t_node_transition *next)
{
	t_node_select_config	config;
	t_node_state			*node;
	int						refresh_stale;

	node = puzzle->cur_node;
	if (node->domain.is_complete || node->domain.is_invalid)
		return (0);
	init_select_config(puzzle, &config);
	refresh_stale = (node->search_policy.branch.cache_refresh
			== CACHE_REFRESH_STALE);
	rebuild_cache_if_stale(puzzle, &config, refresh_stale);
	if (node->search_policy.branch.eligibility == CANDIDATES_LOOKAHEAD)
		return (get_next_lookahead(puzzle, next));
	return (get_best_from_cache(puzzle, next, &config));
}
