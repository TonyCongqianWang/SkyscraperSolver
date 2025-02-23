/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_update.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "grid_update.h"
#include "cell_bitmaps.h"
#include "constraint_checking.h"

void	set_grid_val(t_puzzle *puzzle, int cell_idx, int val, int check)
{
	puzzle->grid_vals[cell_idx] = val;
	puzzle->node_state.num_unset--;
	puzzle->node_state.last_set_idx = cell_idx;
	update_bitmaps(&puzzle->node_state, cell_idx, val);
	if (puzzle->node_state.num_unset == 0)
		puzzle->node_state.is_complete = 1;
	if (check && !puzzle->node_state.is_invalid)
		puzzle->node_state.is_invalid = !check_constraints(puzzle, cell_idx);
}

void	unset_grid_val(t_puzzle *puzzle, int cell_idx)
{
	puzzle->grid_vals[cell_idx] = 0;
}
