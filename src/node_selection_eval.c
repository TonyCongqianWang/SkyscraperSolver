/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_eval.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 10:51:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_eval.h"
#include "grid_availability.h"
#include "cell_bounds.h"

int	set_next_valid_val(t_puzzle *puzzle, t_node_transition *next)
{
	short	cell_val;
	short	cell_ub;

	get_cell_bounds(puzzle->cur_node, next->cell_idx, &cell_val, &cell_ub);
	if (cell_val < next->cell_val)
		cell_val = next->cell_val;
	while (cell_val <= cell_ub)
	{
		if (is_valid_value(puzzle->cur_node, next->cell_idx, cell_val))
		{
			next->cell_val = cell_val;
			return (1);
		}
		cell_val++;
	}
	return (0);
}
