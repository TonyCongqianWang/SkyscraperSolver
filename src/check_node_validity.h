/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   check_node_validity.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/02 23:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/02 23:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CHECK_NODE_VALIDITY_H
# define CHECK_NODE_VALIDITY_H
# include "puzzle_structs.h"

void	push_dirty_constraints(t_node_state *state, int cell_idx);
void	drain_dirty_constraints(t_puzzle *puzzle);

#endif
