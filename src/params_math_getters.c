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
	if (size == 7)
		return (g_weight_cell_constr_ratio_fp_s7);
	if (size == 8)
		return (g_weight_cell_constr_ratio_fp_s8);
	if (size == 9)
		return (g_weight_cell_constr_ratio_fp_s9);
	return (g_weight_cell_constr_ratio_fp);
}

int	get_sel_weight_cell_constr_ratio_fp(int size)
{
	if (size == 7)
		return (g_sel_weight_cell_constr_ratio_fp_s7);
	if (size == 8)
		return (g_sel_weight_cell_constr_ratio_fp_s8);
	if (size == 9)
		return (g_sel_weight_cell_constr_ratio_fp_s9);
	return (g_sel_weight_cell_constr_ratio_fp);
}

double	get_sel_power(int size)
{
	if (size == 7)
		return (g_sel_power_s7);
	if (size == 8)
		return (g_sel_power_s8);
	if (size == 9)
		return (g_sel_power_s9);
	return (g_sel_power);
}

int	get_weight_total_scale_fp(int size)
{
	if (size == 7)
		return (g_weight_total_scale_fp_s7);
	if (size == 8)
		return (g_weight_total_scale_fp_s8);
	if (size == 9)
		return (g_weight_total_scale_fp_s9);
	return (g_weight_total_scale_fp);
}

double	get_global_entropy_unset_bias(int size)
{
	if (size == 7)
		return (g_global_entropy_unset_bias_s7);
	if (size == 8)
		return (g_global_entropy_unset_bias_s8);
	if (size == 9)
		return (g_global_entropy_unset_bias_s9);
	return (g_global_entropy_unset_bias);
}
