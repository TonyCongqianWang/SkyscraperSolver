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
#include "params_int.h"

static int	initial_cell_entropy(t_node_state *node, int size)
{
	int	entropy;
	int	i;

	entropy = 0;
	i = 0;
	while (i < size * size)
	{
		entropy += g_log2_table[(int)node->grid.num_cell_vals[i]]
			* get_weight_cell(size) / ENTROPY_SCALE;
		i++;
	}
	return (entropy);
}

static int	initial_constr_entropy(t_node_state *node, int size)
{
	int	entropy;
	int	i;
	int	v;

	entropy = 0;
	i = 0;
	while (i < 2 * size)
	{
		v = 0;
		while (v < size)
		{
			entropy += g_log2_table[(int)node->constrs
				.num_val_positions[i][v]]
				* get_weight_constr(size) / ENTROPY_SCALE;
			v++;
		}
		i++;
	}
	return (entropy);
}

int	compute_initial_entropy(t_node_state *node, int size)
{
	return (initial_cell_entropy(node, size)
		+ initial_constr_entropy(node, size));
}

int	compute_max_entropy(int size)
{
	return (size * size * g_log2_table[size]
		* (get_weight_cell(size) + 2 * get_weight_constr(size))
		/ ENTROPY_SCALE);
}
