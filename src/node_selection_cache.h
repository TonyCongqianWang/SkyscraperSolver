/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache.h                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef NODE_SELECTION_CACHE_H
# define NODE_SELECTION_CACHE_H

# include "puzzle_structs.h"
# include "strategy_config.h"

int		get_cache_index(t_node_state *node);
void	set_best_val_strat(t_puzzle *puzzle, int idx,
			t_node_transition *best, t_node_select_config *config);
void	build_node_order(t_puzzle *puzzle, t_node_select_config *config);
int		get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
			t_node_select_config *config);
int		get_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
			t_node_select_config *config);

#endif
