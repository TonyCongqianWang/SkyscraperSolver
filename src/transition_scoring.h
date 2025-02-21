/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   transition_scoring.h                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef TRANSITION_SCORING_H
# define TRANSITION_SCORING_H
# include "puzzle_structs.h"

void	score_transition_full(t_node_state *state, t_node_transition *next);
void	score_cell_distance(t_node_state *state, t_node_transition *next);
void	score_transition_constrs(t_node_state *state, t_node_transition *next);
void	transition_add_num_valids(t_node_state *state, t_node_transition *next);

#endif
