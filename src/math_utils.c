/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   math_utils.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/20 18:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/20 18:20:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "math_utils.h"

static double	scale_norm(double *norm)
{
	double	scale;

	scale = 1.0;
	while (*norm > 2.0)
	{
		*norm /= 4.0;
		scale *= 2.0;
	}
	while (*norm < 0.5)
	{
		*norm *= 4.0;
		scale /= 2.0;
	}
	return (scale);
}

double	dsqrt_approx(double x)
{
	double	y;
	double	scale;
	int		iter;

	if (x <= 0.0)
		return (0.0);
	scale = scale_norm(&x);
	y = 0.5 * (1.0 + x);
	iter = 0;
	while (iter < 4)
	{
		y = 0.5 * (y + x / y);
		iter++;
	}
	return (y * scale);
}
