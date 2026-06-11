/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache.h                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 16:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef NODE_SELECTION_CACHE_H
# define NODE_SELECTION_CACHE_H

# include "puzzle_structs.h"
# include "strategy_config.h"

void	set_best_val_strat(t_puzzle *puzzle, int idx,
			t_node_transition *best, t_node_select_config *config);
void	build_node_order(t_puzzle *puzzle, t_node_select_config *config);
void	rebuild_cache_if_stale(t_puzzle *puzzle,
			t_node_select_config *config, int allow_stale_rebuild);
int		get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
			t_node_select_config *config);
int		get_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
			t_node_select_config *config);
int		check_sel_filter(t_node_state *node, int cell_idx,
			int size, int is_selective);
int		resume_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
			int sf_idx, int *i_out);
int		try_cached_entry(t_puzzle *puzzle, t_node_transition *next,
			t_node_order *cache, int i);
int		process_next_entry(t_puzzle *puzzle, t_node_transition *next,
			t_node_select_config *config, int i);
void	init_order_stacks(t_puzzle *puzzle);
void	sync_cache_stacks(t_puzzle *puzzle);

#endif
