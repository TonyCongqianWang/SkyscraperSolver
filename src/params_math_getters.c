/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math_getters.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:35:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:35:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

int	get_weight_cell_constr_ratio_fp(int size)
{
	if (size <= 7)
		return (g_weight_cell_constr_ratio_fp_le7);
	if (size == 8)
		return (g_weight_cell_constr_ratio_fp_s8);
	return (g_weight_cell_constr_ratio_fp_s9);
}

int	get_sel_weight_cell_constr_ratio_fp(int size)
{
	if (size <= 7)
		return (g_sel_weight_cell_constr_ratio_fp_le7);
	if (size == 8)
		return (g_sel_weight_cell_constr_ratio_fp_s8);
	return (g_sel_weight_cell_constr_ratio_fp_s9);
}

double	get_sel_power(int size)
{
	double	u;

	if (size <= 7)
		u = g_sel_power_le7;
	else if (size == 8)
		u = g_sel_power_s8;
	else
		u = g_sel_power_s9;
	return (u * u * u);
}

int	get_weight_total_scale_fp(int size)
{
	if (size <= 7)
		return (g_weight_total_scale_fp_le7);
	if (size == 8)
		return (g_weight_total_scale_fp_s8);
	return (g_weight_total_scale_fp_s9);
}

double	get_global_entropy_unset_bias(int size)
{
	if (size <= 7)
		return (g_global_entropy_unset_bias_le7);
	if (size == 8)
		return (g_global_entropy_unset_bias_s8);
	return (g_global_entropy_unset_bias_s9);
}

double	get_lookahead_score_weight_split0(int size)
{
	if (size <= 7)
		return (g_lookahead_score_weight_split0_le7);
	if (size == 8)
		return (g_lookahead_score_weight_split0_s8);
	return (g_lookahead_score_weight_split0_s9);
}

double	get_lookahead_score_weight_split1(int size)
{
	if (size <= 7)
		return (g_lookahead_score_weight_split1_le7);
	if (size == 8)
		return (g_lookahead_score_weight_split1_s8);
	return (g_lookahead_score_weight_split1_s9);
}
