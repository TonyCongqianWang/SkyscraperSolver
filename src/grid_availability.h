/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_availability.h                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/30 19:48:43 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:17:45 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef GRID_AVAILABILITY_H
# define GRID_AVAILABILITY_H
# include "puzzle_structs.h"

void	decrement_constr_num_valids(t_node_state *state, int cell_idx, int val);
int		get_col_num_valids(t_node_state *state, int cell_idx, int val);
int		get_row_num_valids(t_node_state *state, int cell_idx, int val);
void	decrement_cell_num_valids(t_node_state *state, int idx);
int		get_cell_num_valids(t_node_state *state, int idx);

#endif
