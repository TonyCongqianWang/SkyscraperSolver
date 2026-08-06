/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_score.h                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef NODE_SELECTION_SCORE_H
# define NODE_SELECTION_SCORE_H

# include "puzzle_structs.h"
# include "strategy_config.h"

t_selection_lut	make_selection_lut(int size, double p);
void			score_transition_strat(t_node_state *state,
					t_node_transition *next);
double			calculate_blended_score(t_node_state *node,
					t_node_order *cache, int idx);
void			recalculate_cache_scores(t_node_state *node,
					t_node_order *cache);

#endif
