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

int	compute_max_entropy(int size)
{
	int	cell;
	int	constr;

	cell = get_log2_scaled(size) * get_weight_cell(size) / ENTROPY_SCALE;
	constr = get_log2_scaled(size) * get_weight_constr(size) / ENTROPY_SCALE;
	return (size * size * (cell + 2 * constr));
}
