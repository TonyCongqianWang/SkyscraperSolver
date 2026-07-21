/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_transition.h                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/21 15:28:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/21 15:28:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef NODE_SELECTION_TRANSITION_H
# define NODE_SELECTION_TRANSITION_H
# include "puzzle_structs.h"

int		get_score_family_idx(t_score_family sf);
int		check_sel(t_node_state *node, int idx,
			t_node_select_config *conf);
void	init_node_transition(t_node_transition *tr);
void	sync_cache_stacks(t_puzzle *puzzle);
int		check_sel_filter(t_node_state *node, int cell_idx,
			int size, t_selectivity_level selectivity);

#endif
