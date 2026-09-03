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
extern double	g_global_entropy_unset_bias_le7;
extern double	g_sel_weight_cell_constr_ratio_le7;
extern double	g_sel_power_le7;
extern double	g_lookahead_score_weight_split0_le7;
extern double	g_lookahead_score_weight_split1_le7;
extern double	g_lookahead_entropy_weight_le7;
extern double	g_lookahead_score_age_limit_ratio_le7;

/* Size 8 Math Parameters */
extern double	g_weight_cell_constr_ratio_s8;
extern double	g_weight_total_scale_s8;
extern double	g_global_entropy_unset_bias_s8;
extern double	g_sel_weight_cell_constr_ratio_s8;
extern double	g_sel_power_s8;
extern double	g_lookahead_score_weight_split0_s8;
extern double	g_lookahead_score_weight_split1_s8;
extern double	g_lookahead_entropy_weight_s8;
extern double	g_lookahead_score_age_limit_ratio_s8;

/* Size 9 Math Parameters */
extern double	g_weight_cell_constr_ratio_s9;
extern double	g_weight_total_scale_s9;
extern double	g_global_entropy_unset_bias_s9;
extern double	g_sel_weight_cell_constr_ratio_s9;
extern double	g_sel_power_s9;
extern double	g_lookahead_score_weight_split0_s9;
extern double	g_lookahead_score_weight_split1_s9;
extern double	g_lookahead_entropy_weight_s9;
extern double	g_lookahead_score_age_limit_ratio_s9;

/* Size <= 7 Routing Depth Ratios */
extern double	g_routing_depth_0_ratio_le7;
extern double	g_routing_depth_1_ratio_le7;
extern double	g_routing_depth_2_ratio_le7;
extern double	g_routing_depth_3_ratio_le7;
extern double	g_routing_depth_4_ratio_le7;
extern double	g_routing_depth_5_ratio_le7;
extern double	g_routing_depth_6_ratio_le7;
extern double	g_routing_depth_7_ratio_le7;
extern double	g_routing_depth_8_ratio_le7;

/* Size 8 Routing Depth Ratios */
extern double	g_routing_depth_0_ratio_s8;
extern double	g_routing_depth_1_ratio_s8;
extern double	g_routing_depth_2_ratio_s8;
extern double	g_routing_depth_3_ratio_s8;
extern double	g_routing_depth_4_ratio_s8;
extern double	g_routing_depth_5_ratio_s8;
extern double	g_routing_depth_6_ratio_s8;
extern double	g_routing_depth_7_ratio_s8;
extern double	g_routing_depth_8_ratio_s8;

/* Size 9 Routing Depth Ratios */
extern double	g_routing_depth_0_ratio_s9;
extern double	g_routing_depth_1_ratio_s9;
extern double	g_routing_depth_2_ratio_s9;
extern double	g_routing_depth_3_ratio_s9;
extern double	g_routing_depth_4_ratio_s9;
extern double	g_routing_depth_5_ratio_s9;
extern double	g_routing_depth_6_ratio_s9;
extern double	g_routing_depth_7_ratio_s9;
extern double	g_routing_depth_8_ratio_s9;

/* Size-indexed Accessors */
double			get_weight_cell_constr_ratio(int size);
double			get_weight_total_scale(int size);
double			get_global_entropy_unset_bias(int size);
double			get_sel_weight_cell_constr_ratio(int size);
double			get_sel_power(int size);
double			get_lookahead_score_weight_split0(int size);
double			get_lookahead_score_weight_split1(int size);
double			get_lookahead_entropy_weight(int size);
double			get_lookahead_score_age_limit_ratio(int size);
double			get_routing_depth_ratio(int size, int border_idx);

#endif
