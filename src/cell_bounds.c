/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   cell_bounds.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/30 19:48:43 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:17:45 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "cell_bounds.h"
#include "cell_bitmaps.h"
#include "grid_update.h"
#include "constraint_checking.h"

int	tighten_single_cell_bounds(t_puzzle *puzzle, int idx)
{
	short			cell_val;
	short			cell_ub;
	short			num_valid;
	int				success;
	t_node_state	*node_state;

	node_state = &puzzle->node_state;
	get_cell_bounds(node_state, idx, &cell_val, &cell_ub);
	num_valid = 0;
	success = 0;
	while (cell_val <= cell_ub)
	{
		if (is_valid_value(node_state, idx, cell_val))
		{
			if (check_grid_val_violations(puzzle, idx, cell_val))
				success = 1;
			else
				num_valid++;
		}
		cell_val++;
	}
	set_cell_num_valids(node_state, idx, num_valid);
	return (success);
}

void	update_cell_bounds(t_node_state *state, int idx)
{
	short	lb;
	short	ub;

	lb = 1;
	while (lb < state->size
		&& !is_valid_value(state, idx, lb))
	{
		lb++;
	}
	ub = state->size;
	while (ub > 1
		&& !is_valid_value(state, idx, ub))
	{
		ub--;
	}
	lb &= 0x0F;
	ub = (ub & 0x0F) << 4;
	state->cell_bounds[idx] &= ~(0xFF);
	state->cell_bounds[idx] |= lb;
	state->cell_bounds[idx] |= ub;
}

void	get_cell_bounds(t_node_state *state, int idx, short *lb, short *ub)
{
	*lb = state->cell_bounds[idx] & 0x0F;
	*ub = state->cell_bounds[idx] & 0xF0;
	*ub >>= 4;
}

void	set_cell_num_valids(t_node_state *state, int idx, short n_valids)
{
	n_valids = (n_valids << 8) & 0xF00;
	state->cell_bounds[idx] &= ~0xF00;
	state->cell_bounds[idx] |= n_valids;
}

int	get_cell_num_valids(t_node_state *state, int idx)
{
	int		res;

	res = state->cell_bounds[idx] & 0xF00;
	res >>= 8;
	return (res);
}
