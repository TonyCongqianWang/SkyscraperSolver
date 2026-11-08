/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   strategy_routing.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef STRATEGY_ROUTING_H
# define STRATEGY_ROUTING_H

# include "puzzle_structs.h"
# include "strategy_config.h"

/* prune_strat_routing.c */
int		prune_current_step(t_solver_state *puzzle);

/* sel_strat_routing.c */
void	select_node_select_config(t_solver_state *puzzle,
			t_node_select_config *config);

#endif
