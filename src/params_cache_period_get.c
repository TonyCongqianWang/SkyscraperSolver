/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_cache_period_get.c                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_cache_period.h"

static void	get_le7_periods(double *scales)
{
	scales[0] = g_sel_compact_period_le7;
	scales[1] = g_sel_rescore_period_le7;
	scales[2] = g_sel_blend_period_le7;
	scales[3] = g_sel_sort_period_le7;
	scales[4] = g_sel_line_sort_period_le7;
}

static void	get_s8_periods(double *scales)
{
	scales[0] = g_sel_compact_period_s8;
	scales[1] = g_sel_rescore_period_s8;
	scales[2] = g_sel_blend_period_s8;
	scales[3] = g_sel_sort_period_s8;
	scales[4] = g_sel_line_sort_period_s8;
}

static void	get_s9_periods(double *scales)
{
	scales[0] = g_sel_compact_period_s9;
	scales[1] = g_sel_rescore_period_s9;
	scales[2] = g_sel_blend_period_s9;
	scales[3] = g_sel_sort_period_s9;
	scales[4] = g_sel_line_sort_period_s9;
}

double	get_sel_period_scale(int size)
{
	if (size <= 7)
		return (g_sel_period_scale_le7);
	if (size == 8)
		return (g_sel_period_scale_s8);
	return (g_sel_period_scale_s9);
}

double	get_cache_period_scale(int size, t_order_refresh operation)
{
	double	scales[ORDER_REFRESH_COUNT];

	if (size <= 7)
		get_le7_periods(scales);
	else if (size == 8)
		get_s8_periods(scales);
	else
		get_s9_periods(scales);
	return (scales[operation]);
}
