/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_effective_depth.c                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:35:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:35:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

double	get_num_set_warp(int size, int idx)
{
	if (size <= 7 && idx == 0)
		return (g_num_set_warp_0_le7);
	if (size <= 7 && idx == 1)
		return (g_num_set_warp_1_le7);
	if (size <= 7)
		return (g_num_set_warp_2_le7);
	if (size == 8 && idx == 0)
		return (g_num_set_warp_0_s8);
	if (size == 8 && idx == 1)
		return (g_num_set_warp_1_s8);
	if (size == 8)
		return (g_num_set_warp_2_s8);
	if (idx == 0)
		return (g_num_set_warp_0_s9);
	if (idx == 1)
		return (g_num_set_warp_1_s9);
	return (g_num_set_warp_2_s9);
}

static double	warp_progress(double u, double w0, double w1, double w2)
{
	if (u <= 0.25)
		return (4.0 * u * w0);
	if (u <= 0.50)
		return (w0 + 4.0 * (u - 0.25) * (w1 - w0));
	if (u <= 0.75)
		return (w1 + 4.0 * (u - 0.50) * (w2 - w1));
	return (w2 + 4.0 * (u - 0.75) * (1.0 - w2));
}

double	effective_depth(int size, int depth, int num_unset)
{
	double	d;
	double	s;
	double	alpha;

	d = warp_progress((double)depth / (size * size),
			get_depth_warp(size, 0), get_depth_warp(size, 1),
			get_depth_warp(size, 2));
	s = warp_progress((double)(size * size - num_unset) / (size * size),
			get_num_set_warp(size, 0), get_num_set_warp(size, 1),
			get_num_set_warp(size, 2));
	alpha = g_effective_depth_c0 + g_effective_depth_cd * d
		+ g_effective_depth_cs * s + g_effective_depth_cdd * d * d
		+ g_effective_depth_cds * d * s + g_effective_depth_css * s * s;
	return ((1.0 - alpha) * d + alpha * s);
}
