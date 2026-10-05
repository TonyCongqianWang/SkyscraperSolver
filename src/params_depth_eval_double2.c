/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_depth_eval_double2.c                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/05 15:30:00 by towang            #+#    #+#             */
/*   Updated: 2026/10/05 15:30:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_depth_arrays.h"
#include "params_double.h"

static void	eval_doubles2_part1(int d, const double *w)
{
	double	val;

	val = w[0] * g_constr_local_min_entropy_p00
		+ w[1] * g_constr_local_min_entropy_p25
		+ w[2] * g_constr_local_min_entropy_p50
		+ w[3] * g_constr_local_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_constr_local_min_entropy[d] = val;
	val = w[0] * g_constr_local_max_entropy_p00
		+ w[1] * g_constr_local_max_entropy_p25
		+ w[2] * g_constr_local_max_entropy_p50
		+ w[3] * g_constr_local_max_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_constr_local_max_entropy[d] = val;
}

static void	eval_doubles2_part2(int d, const double *w)
{
	double	val;

	val = w[0] * g_lookahead_gac_local_min_entropy_p00
		+ w[1] * g_lookahead_gac_local_min_entropy_p25
		+ w[2] * g_lookahead_gac_local_min_entropy_p50
		+ w[3] * g_lookahead_gac_local_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_lookahead_gac_local_min_entropy[d] = val;
	val = w[0] * g_lookahead_gac_local_max_entropy_p00
		+ w[1] * g_lookahead_gac_local_max_entropy_p25
		+ w[2] * g_lookahead_gac_local_max_entropy_p50
		+ w[3] * g_lookahead_gac_local_max_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_lookahead_gac_local_max_entropy[d] = val;
}

static void	eval_doubles2_part3(int d, const double *w)
{
	double	val;

	val = w[0] * g_lookahead_constr_local_min_entropy_p00
		+ w[1] * g_lookahead_constr_local_min_entropy_p25
		+ w[2] * g_lookahead_constr_local_min_entropy_p50
		+ w[3] * g_lookahead_constr_local_min_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_lookahead_constr_local_min_entropy[d] = val;
	val = w[0] * g_lookahead_constr_local_max_entropy_p00
		+ w[1] * g_lookahead_constr_local_max_entropy_p25
		+ w[2] * g_lookahead_constr_local_max_entropy_p50
		+ w[3] * g_lookahead_constr_local_max_entropy_p100;
	if (val < 0.0)
		val = 0.0;
	g_depth_lookahead_constr_local_max_entropy[d] = val;
}

void	init_depth_doubles_part2(int d, const double *w)
{
	eval_doubles2_part1(d, w);
	eval_doubles2_part2(d, w);
	eval_doubles2_part3(d, w);
}
