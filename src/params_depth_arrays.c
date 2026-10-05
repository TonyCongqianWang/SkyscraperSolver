/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_depth_arrays.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/03 14:30:00 by towang            #+#    #+#             */
/*   Updated: 2026/09/03 14:30:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_depth_arrays.h"
#include "params_math.h"

int		g_depth_min_entropy[DEPTH_ARRAY_SIZE];
int		g_depth_gac_min_entropy[DEPTH_ARRAY_SIZE];
int		g_depth_constr_min_entropy[DEPTH_ARRAY_SIZE];
int		g_depth_lookahead_continue_min_entropy[DEPTH_ARRAY_SIZE];
int		g_depth_gac_global_min_entropy[DEPTH_ARRAY_SIZE];
int		g_depth_constr_global_min_entropy[DEPTH_ARRAY_SIZE];
int		g_depth_lookahead_gac_global_min_entropy[DEPTH_ARRAY_SIZE];
int		g_depth_lookahead_constr_global_min_entropy[DEPTH_ARRAY_SIZE];

double	g_depth_lookahead_continue_slope[DEPTH_ARRAY_SIZE];
double	g_depth_period_coef_scale[DEPTH_ARRAY_SIZE];
double	g_depth_period_coef_unset[DEPTH_ARRAY_SIZE];
double	g_depth_period_tier_medium_mult[DEPTH_ARRAY_SIZE];
double	g_depth_period_tier_heavy_mult[DEPTH_ARRAY_SIZE];
double	g_depth_gac_local_min_entropy[DEPTH_ARRAY_SIZE];
double	g_depth_gac_local_max_entropy[DEPTH_ARRAY_SIZE];
double	g_depth_constr_local_min_entropy[DEPTH_ARRAY_SIZE];
double	g_depth_constr_local_max_entropy[DEPTH_ARRAY_SIZE];
double	g_depth_lookahead_gac_local_min_entropy[DEPTH_ARRAY_SIZE];
double	g_depth_lookahead_gac_local_max_entropy[DEPTH_ARRAY_SIZE];
double	g_depth_lookahead_constr_local_min_entropy[DEPTH_ARRAY_SIZE];
double	g_depth_lookahead_constr_local_max_entropy[DEPTH_ARRAY_SIZE];

static double	compute_warped_t(double u, int size)
{
	double	w0;
	double	w1;
	double	w2;

	w0 = get_depth_warp(size, 0);
	w1 = get_depth_warp(size, 1);
	w2 = get_depth_warp(size, 2);
	if (u <= 0.25)
		return (4.0 * u * w0);
	else if (u <= 0.50)
		return (w0 + 4.0 * (u - 0.25) * (w1 - w0));
	else if (u <= 0.75)
		return (w1 + 4.0 * (u - 0.50) * (w2 - w1));
	else
		return (w2 + 4.0 * (u - 0.75) * (1.0 - w2));
}

void	init_depth_arrays(int size, int squared_size)
{
	int		d;
	double	u;
	double	t;
	double	w[4];

	d = 0;
	while (d <= squared_size)
	{
		u = (double)d / (double)squared_size;
		t = compute_warped_t(u, size);
		compute_catmull_weights(t, w);
		init_depth_ints_at(d, w);
		init_depth_doubles_part1(d, w);
		init_depth_doubles_part2(d, w);
		d++;
	}
}
