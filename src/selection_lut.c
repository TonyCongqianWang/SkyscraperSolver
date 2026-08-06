/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   selection_lut.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:41:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:41:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_score.h"
#include "math_utils.h"

static double	compute_lut_val(int i, double p)
{
	double	ln_x;

	if (p > 1e-4 || p < -1e-4)
		return ((1.0 - custom_pow(i, p)) / p);
	ln_x = custom_ln(i);
	return (-ln_x - (p * ln_x * ln_x) / 2.0
		- (p * p * ln_x * ln_x * ln_x) / 6.0);
}

t_selection_lut	make_selection_lut(int size, double p)
{
	t_selection_lut	lut;
	int				i;

	lut.values[0] = 0.0;
	i = 1;
	while (i <= 9)
	{
		lut.values[i] = compute_lut_val(i, p);
		i++;
	}
	lut.min_score = lut.values[size];
	return (lut);
}
