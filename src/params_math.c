/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

double	g_num_set_warp_0_le7 = 0.2743;
double	g_num_set_warp_1_le7 = 0.5;
double	g_num_set_warp_2_le7 = 0.75;
double	g_global_entropy_multiplier_le7 = 0.9739;
double	g_num_set_warp_0_s8 = 0.271331232298949;
double	g_num_set_warp_1_s8 = 0.500040585661338;
double	g_num_set_warp_2_s8 = 0.750172633580024;
double	g_global_entropy_multiplier_s8 = 0.998966944478929;
double	g_num_set_warp_0_s9 = 0.260909045665145;
double	g_num_set_warp_1_s9 = 0.52191168724239;
double	g_num_set_warp_2_s9 = 0.729362194654032;
double	g_global_entropy_multiplier_s9 = 0.98270762250719;
double	g_effective_depth_c0 = 0.507961525257627;
double	g_effective_depth_cd = 0.102259411835899;
double	g_effective_depth_cs = -0.0985874330109949;
double	g_effective_depth_cdd = -0.00194048122992632;
double	g_effective_depth_cds = 0.000207834429381094;
double	g_effective_depth_css = 0.000708914246324847;
double	g_weight_cell_constr_ratio_le7 = 0.750210382371435;
double	g_weight_cell_constr_ratio_s8 = 0.750057163912142;
double	g_weight_cell_constr_ratio_s9 = 0.644196589615484;
double	g_sel_weight_cell_constr_ratio_le7 = 0.027865602;
double	g_sel_weight_cell_constr_ratio_s8 = 0;
double	g_sel_weight_cell_constr_ratio_s9 = 0;
double	g_weight_total_scale_le7 = 2827.7419330422;
double	g_weight_total_scale_s8 = 3172.70203149288;
double	g_weight_total_scale_s9 = 2500;
double	g_sel_power_cell_le7 = -0.51874;
double	g_sel_power_cell_s8 = -0.519734118867414;
double	g_sel_power_cell_s9 = -0.528872875630353;
double	g_sel_power_constr_le7 = -0.51972463;
double	g_sel_power_constr_s8 = -0.515355099036316;
double	g_sel_power_constr_s9 = -0.5178227835633;
double	g_lookahead_score_weight_split0_le7 = 0.46758;
double	g_lookahead_score_weight_split0_s8 = 0.46719885;
double	g_lookahead_score_weight_split0_s9 = 0.45847219;
double	g_lookahead_score_weight_split1_le7 = 0.74526;
double	g_lookahead_score_weight_split1_s8 = 0.75154781;
double	g_lookahead_score_weight_split1_s9 = 0.74987568;
double	g_lookahead_entropy_weight_le7 = 0.037873382;
double	g_lookahead_entropy_weight_s8 = 0.0499176054773337;
double	g_lookahead_entropy_weight_s9 = 0.0610652536047558;
double	g_depth_warp_0_le7 = 0.2392;
double	g_depth_warp_0_s8 = 0.249985081355408;
double	g_depth_warp_0_s9 = 0.253335799182131;
double	g_depth_warp_1_le7 = 0.5054;
double	g_depth_warp_1_s8 = 0.505576821176917;
double	g_depth_warp_1_s9 = 0.499929158365865;
double	g_depth_warp_2_le7 = 0.7716;
double	g_depth_warp_2_s8 = 0.74984734606579;
double	g_depth_warp_2_s9 = 0.760574690864289;
double	g_lookahead_score_age_limit_ratio_le7 = 0.088507087;
double	g_lookahead_score_age_limit_ratio_s8 = 0.088520448;
double	g_lookahead_score_age_limit_ratio_s9 = 0.088017684;
