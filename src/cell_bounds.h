/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   cell_bounds.h                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 20:33:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CELL_BOUNDS_H
# define CELL_BOUNDS_H
# include "puzzle_structs.h"

void	update_cell_bounds(t_node_state *state, int idx);
void	get_cell_bounds(t_node_state *state, int idx, short *lb, short *ub);

#endif
