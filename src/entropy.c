/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   entropy.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/15 11:35:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/15 11:35:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "entropy.h"
#include "puzzle_structs.h"

int	entropy_delta_cell(int old_count)
{
	return ((g_log2_table[old_count] - g_log2_table[old_count - 1])
		* g_weight_cell / ENTROPY_SCALE);
}

int	entropy_delta_constr(int old_count)
{
	return ((g_log2_table[old_count] - g_log2_table[old_count - 1])
		* g_weight_constr / ENTROPY_SCALE);
}

int	compute_initial_entropy(t_node_state *node, int size)
{
	int	entropy;
	int	i;
	int	v;

	entropy = 0;
	i = 0;
	while (i < size * size)
	{
		entropy += g_log2_table[(int)node->grid.num_cell_vals[i]]
			* g_weight_cell / ENTROPY_SCALE;
		i++;
	}
	i = 0;
	while (i < 2 * size)
	{
		v = 0;
		while (v < size)
		{
			entropy += g_log2_table[(int)node->constrs
				.num_val_positions[i][v]]
				* g_weight_constr / ENTROPY_SCALE;
			v++;
		}
		i++;
	}
	return (entropy);
}

int	compute_max_entropy(int size)
{
	return (size * size * g_log2_table[size]
		* (g_weight_cell + 2 * g_weight_constr) / ENTROPY_SCALE);
}

int	isqrt_approx(long long n)
{
	long long	x;
	long long	y;

	if (n <= 1)
		return ((int)n);
	x = n;
	y = (x + 1) / 2;
	while (y < x)
	{
		x = y;
		y = (x + n / x) / 2;
	}
	return ((int)x);
}
