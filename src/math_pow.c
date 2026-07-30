/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   math_pow.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:38:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:38:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "math_pow.h"
#include "math_log.h"

static double	taylor_approx(double u)
{
	double	u2;
	double	u3;
	double	u4;
	double	u5;
	double	u6;

	u2 = u * u;
	u3 = u2 * u;
	u4 = u3 * u;
	u5 = u4 * u;
	u6 = u5 * u;
	return (1.0 + u + u2 / 2.0 + u3 / 6.0
		+ u4 / 24.0 + u5 / 120.0 + u6 / 720.0);
}

static double	custom_exp(double y)
{
	double	val;

	val = taylor_approx(y / 32.0);
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
