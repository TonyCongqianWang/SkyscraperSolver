/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_update.h                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 20:46:14 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef GRID_UPDATE_H
# define GRID_UPDATE_H
# include "puzzle_structs.h"

void	set_grid_val(t_node_state *state, int cell_idx, int val, int check);
int		is_cell_empty(t_node_state *state, int cell_idx);
int		is_valid_value(t_node_state *state, int cell_idx, int val);
void	set_value_invalid(t_node_state *state, int cell_idx, int val);
void	update_bitmaps(t_node_state *state, int cell_idx, int val);

#endif
