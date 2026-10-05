/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_depth_cubic.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/05 14:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/10/05 14:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_depth_arrays.h"

static void	compute_hermite_basis(double tau, double *h)
{
	double	tau2;
	double	tau3;

	tau2 = tau * tau;
	tau3 = tau2 * tau;
	h[0] = 2.0 * tau3 - 3.0 * tau2 + 1.0;
	h[1] = tau3 - 2.0 * tau2 + tau;
	h[2] = -2.0 * tau3 + 3.0 * tau2;
	h[3] = tau3 - tau2;
}

static void	eval_seg0(const double *h, double *w)
{
	w[0] = h[0] - h[1] - 0.5 * h[3];
	w[1] = h[2] + h[1];
	w[2] = 0.5 * h[3];
	w[3] = 0.0;
}

static void	eval_seg1(const double *h, double *w)
{
	w[0] = -0.5 * h[1];
	w[1] = h[0] - (1.0 / 3.0) * h[3];
	w[2] = h[2] + 0.5 * h[1];
	w[3] = (1.0 / 3.0) * h[3];
}

static void	eval_seg2(const double *h, double *w)
{
	w[0] = 0.0;
	w[1] = -(2.0 / 3.0) * h[1];
	w[2] = h[0] - h[3];
	w[3] = h[2] + (2.0 / 3.0) * h[1] + h[3];
}

void	compute_catmull_weights(double t, double *w)
{
	double	h[4];

	if (t <= 0.25)
	{
		compute_hermite_basis(4.0 * t, h);
		eval_seg0(h, w);
	}
	else if (t <= 0.50)
	{
		compute_hermite_basis(4.0 * (t - 0.25), h);
		eval_seg1(h, w);
	}
	else
	{
		compute_hermite_basis(2.0 * (t - 0.50), h);
		eval_seg2(h, w);
	}
}
