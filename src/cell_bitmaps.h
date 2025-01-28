/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   cell_bitmaps.h                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 17:12:16 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CELL_BITMAPS_H
# define CELL_BITMAPS_H
# include "puzzle_structs.h"

int		is_valid_value(t_node_state *state, int cell_idx, int val);
void	set_value_invalid(t_node_state *state, int cell_idx, int val);
void	update_bitmaps(t_node_state *state, int cell_idx, int val);

#endif
