/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/29 02:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/29 02:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

/* General Math Parameter Defaults */
int		g_weight_cell_constr_ratio_fp = 4441;
int		g_weight_total_scale_fp = 1135;
double	g_global_entropy_unset_bias = 516.96;

/* Size 7 Math Parameters */
int		g_weight_cell_constr_ratio_fp_s7 = 4437;
int		g_weight_total_scale_fp_s7 = 1151;
double	g_global_entropy_unset_bias_s7 = 580.4968591189568;

/* Size 8 Math Parameters */
int		g_weight_cell_constr_ratio_fp_s8 = 4416;
int		g_weight_total_scale_fp_s8 = 1210;
double	g_global_entropy_unset_bias_s8 = 473.01870528343966;

/* Size 9 Math Parameters */
int		g_weight_cell_constr_ratio_fp_s9 = 4441;
int		g_weight_total_scale_fp_s9 = 1135;
double	g_global_entropy_unset_bias_s9 = 516.96;

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
