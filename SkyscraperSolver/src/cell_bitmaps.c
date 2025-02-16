/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   cell_bitmaps.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 16:54:59 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "puzzle_structs.h"
#include "cell_bitmaps.h"

int	is_valid_value(t_node_state *state, int cell_idx, int val)
{
	int		bitmask;
	short	bitmap;

	bitmask = 1 << (val - 1);
	bitmap = state->valid_val_bmps[cell_idx];
	return (bitmask & bitmap);
}

void	set_value_invalid(t_node_state *state, int cell_idx, int val)
{
	state->valid_val_bmps[cell_idx] &= ~(1 << (val - 1));
}

void	update_bitmaps(t_node_state *state, int cell_idx, int val)
{
	int		counter;
	int		update_idx;

	counter = 0;
	while (counter < state->size)
	{
		update_idx = (cell_idx + counter * state->size);
		update_idx %= state->size * state->size;
		set_value_invalid(state, update_idx, val);
		counter++;
	}
	counter = 0;
	while (counter < state->size)
	{
		update_idx = (cell_idx / state->size) * state->size;
		update_idx += ((cell_idx + counter) % state->size);
		set_value_invalid(state, update_idx, val);
		counter++;
	}
}
