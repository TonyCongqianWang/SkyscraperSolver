/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   math_sqrt.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:38:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:38:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "math_sqrt.h"

static double	scale_down(double *norm)
{
	double	scale;

	scale = 1.0;
	while (*norm > 2.0)
	{
		*norm /= 4.0;
		scale *= 2.0;
	}
	return (scale);
}

static double	scale_up(double *norm)
{
	double	scale;

	scale = 1.0;
	while (*norm < 0.5)
	{
		*norm *= 4.0;
		scale /= 2.0;
	}
	return (scale);
}

static double	scale_norm(double *norm)
{
	if (*norm > 2.0)
		return (scale_down(norm));
	if (*norm < 0.5)
		return (scale_up(norm));
	return (1.0);
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

double	dpow075_approx(double x)
{
	double	s;

	if (x <= 0.0)
		return (0.0);
	s = dsqrt_approx(x);
	return (s * dsqrt_approx(s));
}
