/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   entropy_delta.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/20 18:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/20 18:20:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "entropy.h"

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

int	compute_constr_entropy(t_node_state *node, int idx, int size)
{
	int	entropy;
	int	v;

	entropy = 0;
	v = 0;
	while (v < size)
	{
		entropy += g_log2_table[(int)node->constrs.num_val_positions[idx][v]]
			* g_weight_constr / ENTROPY_SCALE;
		v++;
	}
	return (entropy);
}

double	get_relative_constr_entropy(t_node_state *node, int idx, int size)
{
	int	current_entropy;
	int	max_entropy;

	current_entropy = compute_constr_entropy(node, idx, size);
	max_entropy = size * g_log2_table[size] * g_weight_constr / ENTROPY_SCALE;
	if (max_entropy <= 0)
		return (0.0);
	return ((double)current_entropy / max_entropy);
}
