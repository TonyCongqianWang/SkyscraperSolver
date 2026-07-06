/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_interface.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/06 16:44:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/06 16:44:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "grid_interface.h"
#include "grid_manipulation.h"
#include "check_node_validity.h"

int	set_cell_val(t_puzzle *puzzle, int cell_idx, int val, t_check_mode mode)
{
	set_grid_val_internal(puzzle->cur_node, cell_idx, val, 0);
	if (mode != CHECK_NONE)
		return (check_node_validity(puzzle, mode));
	return (!puzzle->cur_node->is_invalid);
}

int	set_cell_invalid(t_puzzle *puzzle, int cell_idx, int val, t_check_mode mode)
{
	set_value_invalid_internal(puzzle->cur_node, cell_idx, val);
	if (mode != CHECK_NONE)
		return (check_node_validity(puzzle, mode));
	return (!puzzle->cur_node->is_invalid);
}

int	set_cell_vals_batch(t_puzzle *puzzle, const t_grid_update *updates,
		int count, t_check_mode mode)
{
	int	i;

	i = 0;
	while (i < count && !puzzle->cur_node->is_invalid)
	{
		set_grid_val_internal(puzzle->cur_node, updates[i].cell_idx,
			updates[i].val, 0);
		i++;
	}
	if (mode != CHECK_NONE)
		return (check_node_validity(puzzle, mode));
	return (!puzzle->cur_node->is_invalid);
}

int	set_cells_invalid_batch(t_puzzle *puzzle, const t_grid_update *updates,
		int count, t_check_mode mode)
{
	int	i;

	i = 0;
	while (i < count && !puzzle->cur_node->is_invalid)
	{
		set_value_invalid_internal(puzzle->cur_node, updates[i].cell_idx,
			updates[i].val);
		i++;
	}
	if (mode != CHECK_NONE)
		return (check_node_validity(puzzle, mode));
	return (!puzzle->cur_node->is_invalid);
}
