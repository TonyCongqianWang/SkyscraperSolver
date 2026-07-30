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

int	entropy_delta_cell(int old_count, int size)
{
	return ((get_log2_scaled(old_count) - get_log2_scaled(old_count - 1))
		* get_weight_cell(size) / ENTROPY_SCALE);
}

int	entropy_delta_constr(int old_count, int size)
{
	return ((get_log2_scaled(old_count) - get_log2_scaled(old_count - 1))
		* get_weight_constr(size) / ENTROPY_SCALE);
}

int	compute_constr_entropy(t_node_state *node, int idx, int size)
{
	int	entropy;
	int	v;
	int	pos_count;

	entropy = 0;
	v = 0;
	while (v < size)
	{
		pos_count = (int)node->constrs.num_val_positions[idx][v];
		entropy += get_log2_scaled(pos_count)
			* get_weight_constr(size) / ENTROPY_SCALE;
		v++;
	}
	return (entropy);
}

double	get_relative_constr_entropy(t_node_state *node, int idx, int size)
{
	int	current_entropy;

	current_entropy = compute_constr_entropy(node, idx, size);
	if (node->puzzle->constr_max_entropy <= 0)
		return (0.0);
	return ((double)current_entropy / node->puzzle->constr_max_entropy);
}
