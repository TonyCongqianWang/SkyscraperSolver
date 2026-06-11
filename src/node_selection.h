/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection.h                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 16:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef NODE_SELECTION_H
# define NODE_SELECTION_H

# include "puzzle_structs.h"
# include "strategy_config.h"

int		try_get_best_transition(t_puzzle *puzzle, t_node_transition *next);
int		try_get_next_transition(t_puzzle *puzzle, t_node_transition *next);
void	init_node_transition(t_node_transition *tr);

#endif
