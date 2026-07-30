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

#ifdef LOOKAHEAD_SCORE_FAMILY

static const t_score_family			g_lh_score_family = LOOKAHEAD_SCORE_FAMILY;
static const int					g_lh_score_family_defined = 1;

#else

static const t_score_family			g_lh_score_family = SCORE_BRANCHING;
static const int					g_lh_score_family_defined = 0;

#endif

#ifdef LOOKAHEAD_CRITERION

static const t_selection_criterion	g_lh_criterion = LOOKAHEAD_CRITERION;
static const int					g_lh_criterion_defined = 1;

#else

static const t_selection_criterion	g_lh_criterion = SELECT_MAX;
static const int					g_lh_criterion_defined = 0;

#endif

static void	init_select_config(t_puzzle *puzzle, t_node_transition *next,
				t_node_select_config *config)
{
	t_node_state	*node;

	node = puzzle->cur_node;
	select_node_select_config(puzzle, config);
	if (node->is_in_lookahead_select)
	{
		config->start_cell_idx = next->cell_idx;
		config->start_cell_val = 1;
		if (next->cell_idx >= 0)
			config->start_cell_val = next->cell_val + 1;
		config->selectivity = node->lookahead_selectivity;
		if (g_lh_score_family_defined)
			config->score_family = g_lh_score_family;
		if (g_lh_criterion_defined)
			config->criterion = g_lh_criterion;
	}
}

int	try_get_best_transition(t_puzzle *puzzle, t_node_transition *next)
{
	t_node_select_config	config;

	init_select_config(puzzle, next, &config);
	rebuild_cache_if_stale(puzzle, &config, 1);
	return (get_best_from_cache(puzzle, next, &config));
}

int	try_get_next_transition(t_puzzle *puzzle, t_node_transition *next)
{
	t_node_select_config	config;
	t_node_state			*node;

	node = puzzle->cur_node;
	if (node->is_complete || node->is_invalid)
		return (0);
	init_select_config(puzzle, next, &config);
	rebuild_cache_if_stale(puzzle, &config, 0);
	return (get_next_from_cache(puzzle, next, &config));
}
