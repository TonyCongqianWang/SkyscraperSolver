/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

int		g_weight_cell_constr_ratio_fp = 5561;
int		g_weight_cell_constr_ratio_fp_s7 = 5561;
int		g_weight_cell_constr_ratio_fp_s8 = 5408;
int		g_weight_cell_constr_ratio_fp_s9 = 5349;
int		g_sel_weight_cell_constr_ratio_fp = 8192;
int		g_sel_weight_cell_constr_ratio_fp_s7 = 8192;
int		g_sel_weight_cell_constr_ratio_fp_s8 = 8192;
int		g_sel_weight_cell_constr_ratio_fp_s9 = 8192;
int		g_weight_total_scale_fp = 990;
int		g_weight_total_scale_fp_s7 = 990;
int		g_weight_total_scale_fp_s8 = 934;
int		g_weight_total_scale_fp_s9 = 1092;
double	g_global_entropy_unset_bias = 535.58782;
double	g_global_entropy_unset_bias_s7 = 535.58782;
double	g_global_entropy_unset_bias_s8 = 503.709773;
double	g_global_entropy_unset_bias_s9 = 515.614181;

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
