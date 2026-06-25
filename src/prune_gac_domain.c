/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac_domain.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_gac_domain.h"
#include "grid_manipulation.h"
#include "grid_availability.h"

int	count_bits(int bmp)
{
	int	count;

	count = 0;
	while (bmp > 0)
	{
		if (bmp & 1)
			count++;
		bmp >>= 1;
	}
	return (count);
}

void	eliminate_bmp_vals(t_node_state *state, int cell_idx, int u_bmp)
{
	int	val;

	val = 1;
	while (val <= state->size)
	{
		if (u_bmp & (1 << (val - 1)))
			set_value_invalid(state, cell_idx, val);
		val++;
	}
}

void	keep_only_values(t_node_state *state, int cell_idx, int keep_mask)
{
	int	val;

	val = 1;
	while (val <= state->size)
	{
		if (!(keep_mask & (1 << (val - 1))))
			set_value_invalid(state, cell_idx, val);
		val++;
	}
}

void	get_value_cells(t_node_state *state, int *cells, int count,
			int *value_cells)
{
	int	val;
	int	i;

	val = 1;
	while (val <= state->size)
	{
		value_cells[val - 1] = 0;
		i = 0;
		while (i < count)
		{
			if (is_valid_value(state, cells[i], val))
				value_cells[val - 1] |= (1 << i);
			i++;
		}
		val++;
	}
}
