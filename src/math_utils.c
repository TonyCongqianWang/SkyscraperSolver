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

double	dpow075_approx(double x)
{
	double	s;

	if (x <= 0.0)
		return (0.0);
	s = dsqrt_approx(x);
	return (s * dsqrt_approx(s));
}

double	custom_ln(int x)
{
	static const double	g_ln_table[10] = {
		0.0,
		0.0,
		0.6931471805599453,
		1.0986122886681096,
		1.3862943611198906,
		1.6094379124341003,
		1.791759469228055,
		1.9459101490553132,
		2.0794415416798357,
		2.1972245773362196
	};

	if (x < 1 || x > 9)
		return (0.0);
	return (g_ln_table[x]);
}

static double	custom_exp(double y)
{
	double	u;
	double	u2;
	double	u3;
	double	u4;
	double	u5;
	double	u6;
	double	val;

	u = y / 32.0;
	u2 = u * u;
	u3 = u2 * u;
	u4 = u3 * u;
	u5 = u4 * u;
	u6 = u5 * u;
	val = 1.0 + u + u2 / 2.0 + u3 / 6.0 + u4 / 24.0 + u5 / 120.0 + u6 / 720.0;
	val *= val;
	val *= val;
	val *= val;
	val *= val;
	val *= val;
	return (val);
}

double	custom_pow(int x, double p)
{
	double	ln_x;

	if (x <= 1)
		return (1.0);
	ln_x = custom_ln(x);
	return (custom_exp(p * ln_x));
}
