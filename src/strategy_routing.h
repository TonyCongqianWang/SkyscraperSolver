/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   strategy_routing.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef STRATEGY_ROUTING_H
# define STRATEGY_ROUTING_H

# include "puzzle_structs.h"
# include "strategy_config.h"

void	select_prune_config(t_puzzle *puzzle, t_prune_config *config);
void	select_node_select_config(t_puzzle *puzzle,
			t_node_select_config *config);

#endif
