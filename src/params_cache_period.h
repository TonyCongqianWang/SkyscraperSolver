/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_cache_period.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_CACHE_PERIOD_H
# define PARAMS_CACHE_PERIOD_H

# include "strategy_config.h"

extern double	g_sel_period_scale_le7;
extern double	g_sel_period_scale_s8;
extern double	g_sel_period_scale_s9;
extern double	g_sel_compact_period_le7;
extern double	g_sel_compact_period_s8;
extern double	g_sel_compact_period_s9;
extern double	g_sel_rescore_period_le7;
extern double	g_sel_rescore_period_s8;
extern double	g_sel_rescore_period_s9;
extern double	g_sel_blend_period_le7;
extern double	g_sel_blend_period_s8;
extern double	g_sel_blend_period_s9;
extern double	g_sel_sort_period_le7;
extern double	g_sel_sort_period_s8;
extern double	g_sel_sort_period_s9;
extern double	g_sel_line_sort_period_le7;
extern double	g_sel_line_sort_period_s8;
extern double	g_sel_line_sort_period_s9;

double	get_sel_period_scale(int size);
double	get_cache_period_scale(int size, t_order_refresh operation);

#endif
