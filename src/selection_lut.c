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

t_selection_lut	make_selection_lut(double p)
{
	t_selection_lut	lut;
	int				i;
	double			val;
	double			ln_x;

	lut.values[0] = 0.0;
	i = 1;
	while (i <= 9)
	{
		if (p > 1e-4 || p < -1e-4)
			val = (1.0 - custom_pow(i, p)) / p;
		else
		{
			ln_x = custom_ln(i);
			val = -ln_x - (p * ln_x * ln_x) / 2.0
				- (p * p * ln_x * ln_x * ln_x) / 6.0;
		}
		lut.values[i] = val;
		i++;
	}
	return (lut);
}
