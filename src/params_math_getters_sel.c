/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math_getters_sel.c                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/17 14:12:00 by towang            #+#    #+#             */
/*   Updated: 2026/10/17 14:12:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

double	get_sel_weight_cell_constr_ratio(int size)
{
	if (size <= 7)
		return (g_sel_weight_cell_constr_ratio_le7);
	if (size == 8)
		return (g_sel_weight_cell_constr_ratio_s8);
	return (g_sel_weight_cell_constr_ratio_s9);
}

double	get_sel_power_cell(int size)
{
	double	u;

	if (size <= 7)
		u = g_sel_power_cell_le7;
	else if (size == 8)
		u = g_sel_power_cell_s8;
	else
		u = g_sel_power_cell_s9;
	return (u * u * u);
}

double	get_sel_power_constr(int size)
{
	double	u;

	if (size <= 7)
		u = g_sel_power_constr_le7;
	else if (size == 8)
		u = g_sel_power_constr_s8;
	else
		u = g_sel_power_constr_s9;
	return (u * u * u);
}
