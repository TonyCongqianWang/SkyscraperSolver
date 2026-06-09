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

void	score_transition_strat(t_node_state *state, t_node_transition *next,
			t_score_family family);

#endif
