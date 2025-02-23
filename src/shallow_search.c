/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   shallow_search.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "shallow_search.h"
#include "grid_update.h"
#include "cell_bitmaps.h"
#include "cell_bounds.h"
#include "puzzle_solver.h"

void	tighten_grid_cell_bounds(t_puzzle *puzzle, int depth)
{
	int			cell_idx;
	int			reiterate;

	reiterate = 1;
	while (reiterate)
	{
		cell_idx = 0;
		reiterate = 0;
		while (cell_idx < puzzle->size * puzzle->size
			&& !puzzle->node_state.is_invalid)
		{
			if (is_cell_empty(puzzle, cell_idx))
				reiterate |= tighten_cell_bounds(puzzle, cell_idx, depth);
			cell_idx++;
		}
	}
}

int	tighten_cell_bounds(t_puzzle *puzzle, int idx, int depth)
{
	short			cell_val;
	short			cell_ub;
	int				success;
	t_node_state	*node_state;

	node_state = &puzzle->node_state;
	get_cell_bounds(node_state, idx, &cell_val, &cell_ub);
	success = 0;
	while (cell_val <= cell_ub)
	{
		if (is_valid_value(node_state, idx, cell_val))
		{
			if (!check_val_validity(puzzle, idx, cell_val, depth))
			{
				set_value_invalid(node_state, idx, cell_val);
				success = 1;
			}
		}
		cell_val++;
	}
	return (success);
}

int	check_val_validity(t_puzzle *puzzle, int cell_idx, int val, int depth)
{
	t_node_state	old_state;
	int				is_valid;

	old_state = puzzle->node_state;
	puzzle->node_state.is_sub_state = 1;
	set_grid_val(puzzle, cell_idx, val, 1);
	is_valid = tree_search(puzzle, depth);
	puzzle->node_state = old_state;
	return (is_valid);
}
