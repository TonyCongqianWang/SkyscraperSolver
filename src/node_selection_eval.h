/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_eval.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef NODE_SELECTION_EVAL_H
# define NODE_SELECTION_EVAL_H

# include "puzzle_structs.h"
# include "strategy_config.h"

int		set_next_valid_val(t_puzzle *puzzle, t_node_transition *next);
void	sort_node_order(t_node_transition *entries, int count,
			t_selection_criterion criterion);
void	sort_node_order_meta(t_node_transition *entries,
			t_transition_meta *meta, int count,
			t_selection_criterion criterion);
void	compact_and_sort_cache(t_node_state *node, t_node_order *cache,
			t_selection_criterion criterion);

#endif
