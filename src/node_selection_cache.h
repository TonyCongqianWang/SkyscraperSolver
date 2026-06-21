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

typedef struct s_best_search_ctx
{
	t_node_transition		*next;
	t_node_transition		*best;
	t_node_select_config	*config;
	double					best_possible;
}	t_best_search_ctx;

/* node_selection_cache.c */
void	build_node_order(t_puzzle *puzzle, t_node_select_config *config);

/* node_selection_cache_api.c */
void	rebuild_cache_if_stale(t_puzzle *puzzle,
			t_node_select_config *config, int allow_stale_rebuild);
int		get_best_from_cache(t_puzzle *puzzle, t_node_transition *next,
			t_node_select_config *config);
int		get_next_from_cache(t_puzzle *puzzle, t_node_transition *next,
			t_node_select_config *config);
void	init_order_stacks(t_puzzle *puzzle);
int		get_cell_priority_pass(t_node_state *node, int cell_idx, int size);

/* node_selection_cache_helper.c */
int		try_cached_entry(t_puzzle *puzzle, t_node_transition *next,
			t_node_order *cache, int i);
void	collect_cache_entries(t_puzzle *puzzle, t_node_order *cache,
			t_node_select_config *config);

/* node_selection_utils.c */
void	sync_cache_stacks(t_puzzle *puzzle);
int		check_sel_filter(t_node_state *node, int cell_idx,
			int size, t_selectivity_level selectivity);

#endif
