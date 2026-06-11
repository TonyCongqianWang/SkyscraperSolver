/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection.h                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef NODE_SELECTION_H
# define NODE_SELECTION_H
# include "puzzle_structs.h"
# include "strategy_config.h"

# ifdef LOOKAHEAD_SCORE_FAMILY
static const t_score_family			g_lh_score_family = LOOKAHEAD_SCORE_FAMILY;
static const int					g_lh_score_family_defined = 1;
# else
static const t_score_family			g_lh_score_family = SCORE_BRANCHING;
static const int					g_lh_score_family_defined = 0;
# endif

# ifdef LOOKAHEAD_CRITERION
static const t_selection_criterion	g_lh_criterion = LOOKAHEAD_CRITERION;
static const int					g_lh_criterion_defined = 1;
# else
static const t_selection_criterion	g_lh_criterion = SELECT_MAX;
static const int					g_lh_criterion_defined = 0;
# endif

int		try_get_best_transition(t_puzzle *puzzle, t_node_transition *next);
int		try_get_next_transition(t_puzzle *puzzle, t_node_transition *next);
void	init_node_transition(t_node_transition *tr);

#endif
