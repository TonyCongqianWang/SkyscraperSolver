/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_depth_eval_double1.c                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/05 15:30:00 by towang            #+#    #+#             */
/*   Updated: 2026/10/05 15:30:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_depth_arrays.h"
#include "params_double.h"

static void	eval_doubles1_part1(int d, const double *w)
{
	double	val;

	val = w[0] * g_lookahead_continue_slope_p00
		+ w[1] * g_lookahead_continue_slope_p25
		+ w[2] * g_lookahead_continue_slope_p50
		+ w[3] * g_lookahead_continue_slope_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_lookahead_continue_slope[d] = val;
	val = w[0] * g_period_coef_scale_p00 + w[1] * g_period_coef_scale_p25
		+ w[2] * g_period_coef_scale_p50 + w[3] * g_period_coef_scale_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_period_coef_scale[d] = val;
}

static void	eval_doubles1_part2(int d, const double *w)
{
	double	val;

	val = w[0] * g_period_coef_unset_p00 + w[1] * g_period_coef_unset_p25
		+ w[2] * g_period_coef_unset_p50 + w[3] * g_period_coef_unset_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_period_coef_unset[d] = val;
	val = w[0] * g_period_tier_medium_mult_p00
		+ w[1] * g_period_tier_medium_mult_p25
		+ w[2] * g_period_tier_medium_mult_p50
		+ w[3] * g_period_tier_medium_mult_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_period_tier_medium_mult[d] = val;
}

static void	eval_doubles1_part3(int d, const double *w)
{
	double	val;

	val = w[0] * g_period_tier_heavy_mult_p00
		+ w[1] * g_period_tier_heavy_mult_p25
		+ w[2] * g_period_tier_heavy_mult_p50
		+ w[3] * g_period_tier_heavy_mult_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_period_tier_heavy_mult[d] = val;
	val = w[0] * g_gac_local_min_entropy_p00
		+ w[1] * g_gac_local_min_entropy_p25
		+ w[2] * g_gac_local_min_entropy_p50
		+ w[3] * g_gac_local_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_gac_local_min_entropy[d] = val;
}

static void	eval_doubles1_part4(int d, const double *w)
{
	double	val;

	val = w[0] * g_gac_local_max_entropy_p00
		+ w[1] * g_gac_local_max_entropy_p25
		+ w[2] * g_gac_local_max_entropy_p50
		+ w[3] * g_gac_local_max_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_gac_local_max_entropy[d] = val;
}

void	init_depth_doubles_part1(int d, const double *w)
{
	eval_doubles1_part1(d, w);
	eval_doubles1_part2(d, w);
	eval_doubles1_part3(d, w);
	eval_doubles1_part4(d, w);
}
