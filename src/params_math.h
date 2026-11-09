/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math.h                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_MATH_H
# define PARAMS_MATH_H

/* Size <= 7 Math Parameters */
extern double	g_weight_cell_constr_ratio_le7;
extern double	g_weight_total_scale_le7;
extern double	g_sel_weight_cell_constr_ratio_le7;
extern double	g_sel_power_cell_le7;
extern double	g_sel_power_constr_le7;
extern double	g_lookahead_score_weight_split0_le7;
extern double	g_lookahead_score_weight_split1_le7;
extern double	g_lookahead_entropy_weight_le7;
extern double	g_lookahead_score_age_limit_ratio_le7;

/* Size 8 Math Parameters */
extern double	g_weight_cell_constr_ratio_s8;
extern double	g_weight_total_scale_s8;
extern double	g_sel_weight_cell_constr_ratio_s8;
extern double	g_sel_power_cell_s8;
extern double	g_sel_power_constr_s8;
extern double	g_lookahead_score_weight_split0_s8;
extern double	g_lookahead_score_weight_split1_s8;
extern double	g_lookahead_entropy_weight_s8;
extern double	g_lookahead_score_age_limit_ratio_s8;

/* Size 9 Math Parameters */
extern double	g_weight_cell_constr_ratio_s9;
extern double	g_weight_total_scale_s9;
extern double	g_sel_weight_cell_constr_ratio_s9;
extern double	g_sel_power_cell_s9;
extern double	g_sel_power_constr_s9;
extern double	g_lookahead_score_weight_split0_s9;
extern double	g_lookahead_score_weight_split1_s9;
extern double	g_lookahead_entropy_weight_s9;
extern double	g_lookahead_score_age_limit_ratio_s9;

/* Size <= 7 Routing Depth Ratios */
/* Size Depth Warp Parameters (u = 0.25, 0.50, 0.75) */
extern double	g_depth_warp_0_le7;
extern double	g_depth_warp_1_le7;
extern double	g_depth_warp_2_le7;
extern double	g_depth_warp_0_s8;
extern double	g_depth_warp_1_s8;
extern double	g_depth_warp_2_s8;
extern double	g_depth_warp_0_s9;
extern double	g_depth_warp_1_s9;
extern double	g_depth_warp_2_s9;

extern double	g_num_set_warp_0_le7;
extern double	g_num_set_warp_1_le7;
extern double	g_num_set_warp_2_le7;
extern double	g_global_entropy_multiplier_le7;
extern double	g_num_set_warp_0_s8;
extern double	g_num_set_warp_1_s8;
extern double	g_num_set_warp_2_s8;
extern double	g_global_entropy_multiplier_s8;
extern double	g_num_set_warp_0_s9;
extern double	g_num_set_warp_1_s9;
extern double	g_num_set_warp_2_s9;
extern double	g_global_entropy_multiplier_s9;
extern double	g_effective_depth_c0;
extern double	g_effective_depth_cd;
extern double	g_effective_depth_cs;
extern double	g_effective_depth_cdd;
extern double	g_effective_depth_cds;
extern double	g_effective_depth_css;

/* Size-indexed Accessors */
double			get_weight_cell_constr_ratio(int size);
double			get_weight_total_scale(int size);
double			get_global_entropy_multiplier(int size);
double			get_sel_weight_cell_constr_ratio(int size);
double			get_sel_power_cell(int size);
double			get_sel_power_constr(int size);
double			get_lookahead_score_weight_split0(int size);
double			get_lookahead_score_weight_split1(int size);
double			get_lookahead_entropy_weight(int size);
double			get_lookahead_score_age_limit_ratio(int size);
double			get_depth_warp(int size, int idx);

double			get_num_set_warp(int size, int idx);
double			effective_depth(int size, int depth, int num_unset);

#endif
