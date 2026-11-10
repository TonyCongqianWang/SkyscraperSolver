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

static const double	g_schedule_knots[SCHEDULE_KNOT_COUNT] = {
	0.0, 0.015625, 0.25, 0.50, 1.0
};

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

static void	add_tangent(double *w, double coefficient, int left, int right)
{
	double	factor;

	if (left < 0)
		left = 0;
	if (right >= SCHEDULE_KNOT_COUNT)
		right = SCHEDULE_KNOT_COUNT - 1;
	factor = coefficient / (g_schedule_knots[right] - g_schedule_knots[left]);
	w[left] -= factor;
	w[right] += factor;
}

void	compute_catmull_weights(double t, double *w)
{
	double	h[4];
	double	width;
	int		segment;
	int		i;

	segment = 0;
	while (segment < SCHEDULE_KNOT_COUNT - 2
		&& t > g_schedule_knots[segment + 1])
		segment++;
	width = g_schedule_knots[segment + 1] - g_schedule_knots[segment];
	compute_hermite_basis((t - g_schedule_knots[segment]) / width, h);
	i = -1;
	while (++i < SCHEDULE_KNOT_COUNT)
		w[i] = 0.0;
	w[segment] = h[0];
	w[segment + 1] = h[2];
	add_tangent(w, h[1] * width, segment - 1, segment + 1);
	add_tangent(w, h[3] * width, segment, segment + 2);
}
