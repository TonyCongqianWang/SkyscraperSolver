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
# include "grid_interface.h"

void	push_dirty_constraints(t_node_state *state, int cell_idx);
int		check_node_validity(t_puzzle *puzzle, t_check_mode mode);

#endif
