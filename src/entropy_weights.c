/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   entropy_weights.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/28 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/28 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "entropy.h"
#include "params_math.h"

int	get_weight_cell(int size)
{
	double	scale;
	double	ratio;

	scale = get_weight_total_scale(size);
	ratio = get_weight_cell_constr_ratio(size);
	return ((int)(scale * ratio));
}

int	get_weight_constr(int size)
{
	double	scale;
	double	ratio;

	scale = get_weight_total_scale(size);
	ratio = get_weight_cell_constr_ratio(size);
	return ((int)(scale * (1.0 - ratio) / 2.0));
}
