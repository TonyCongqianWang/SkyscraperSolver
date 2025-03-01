/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_manipulation.h                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 20:46:14 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef GRID_MANIPULATION_H
# define GRID_MANIPULATION_H
# include "puzzle_structs.h"

void	set_grid_val(t_node_state *state, int cell_idx, int val, int check);
void	set_value_invalid(t_node_state *state, int cell_idx, int val);

#endif
