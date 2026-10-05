/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_depth_eval_int.c                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/05 15:30:00 by towang            #+#    #+#             */
/*   Updated: 2026/10/05 15:30:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_depth_arrays.h"
#include "params_int.h"

static void	eval_ints_part1(int d, const double *w)
{
	double	val;

	val = w[0] * g_min_entropy_p00 + w[1] * g_min_entropy_p25
		+ w[2] * g_min_entropy_p50 + w[3] * g_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_min_entropy[d] = (int)(val + 0.5);
	val = w[0] * g_gac_min_entropy_p00 + w[1] * g_gac_min_entropy_p25
		+ w[2] * g_gac_min_entropy_p50 + w[3] * g_gac_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_gac_min_entropy[d] = (int)(val + 0.5);
}

static void	eval_ints_part2(int d, const double *w)
{
	double	val;

	val = w[0] * g_constr_min_entropy_p00 + w[1] * g_constr_min_entropy_p25
		+ w[2] * g_constr_min_entropy_p50 + w[3] * g_constr_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_constr_min_entropy[d] = (int)(val + 0.5);
	val = w[0] * g_lookahead_continue_min_entropy_p00
		+ w[1] * g_lookahead_continue_min_entropy_p25
		+ w[2] * g_lookahead_continue_min_entropy_p50
		+ w[3] * g_lookahead_continue_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_lookahead_continue_min_entropy[d] = (int)(val + 0.5);
}

static void	eval_ints_part3(int d, const double *w)
{
	double	val;

	val = w[0] * g_gac_global_min_entropy_p00
		+ w[1] * g_gac_global_min_entropy_p25
		+ w[2] * g_gac_global_min_entropy_p50
		+ w[3] * g_gac_global_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_gac_global_min_entropy[d] = (int)(val + 0.5);
	val = w[0] * g_constr_global_min_entropy_p00
		+ w[1] * g_constr_global_min_entropy_p25
		+ w[2] * g_constr_global_min_entropy_p50
		+ w[3] * g_constr_global_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_constr_global_min_entropy[d] = (int)(val + 0.5);
}

static void	eval_ints_part4(int d, const double *w)
{
	double	val;

	val = w[0] * g_lookahead_gac_global_min_entropy_p00
		+ w[1] * g_lookahead_gac_global_min_entropy_p25
		+ w[2] * g_lookahead_gac_global_min_entropy_p50
		+ w[3] * g_lookahead_gac_global_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_lookahead_gac_global_min_entropy[d] = (int)(val + 0.5);
	val = w[0] * g_lookahead_constr_global_min_entropy_p00
		+ w[1] * g_lookahead_constr_global_min_entropy_p25
		+ w[2] * g_lookahead_constr_global_min_entropy_p50
		+ w[3] * g_lookahead_constr_global_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_lookahead_constr_global_min_entropy[d] = (int)(val + 0.5);
}

void	init_depth_ints_at(int d, const double *w)
{
	eval_ints_part1(d, w);
	eval_ints_part2(d, w);
	eval_ints_part3(d, w);
	eval_ints_part4(d, w);
}
