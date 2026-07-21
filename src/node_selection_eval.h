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
void	set_best_val_strat(t_puzzle *puzzle, int idx,
			t_node_transition *best, t_node_select_config *config);
void	sort_node_order(t_node_transition *entries, int count,
			t_selection_criterion criterion);
int		scan_best_live(t_puzzle *puzzle, t_node_transition *next,
			t_node_select_config *config);

#endif
