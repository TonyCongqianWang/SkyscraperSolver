/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_depth_arrays.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/03 14:30:00 by towang            #+#    #+#             */
/*   Updated: 2026/09/03 14:30:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_depth_arrays.h"
#include "params_int.h"
#include "params_double.h"
#include "params_math.h"

const int		*g_depth_min_entropy[10] = {
	&g_depth_0_min_entropy,
	&g_depth_1_min_entropy,
	&g_depth_2_min_entropy,
	&g_depth_3_min_entropy,
	&g_depth_4_min_entropy,
	&g_depth_5_min_entropy,
	&g_depth_6_min_entropy,
	&g_depth_7_min_entropy,
	&g_depth_8_min_entropy,
	&g_depth_9_min_entropy
};

const int		*g_depth_gac_min_entropy[10] = {
	&g_depth_0_gac_min_entropy,
	&g_depth_1_gac_min_entropy,
	&g_depth_2_gac_min_entropy,
	&g_depth_3_gac_min_entropy,
	&g_depth_4_gac_min_entropy,
	&g_depth_5_gac_min_entropy,
	&g_depth_6_gac_min_entropy,
	&g_depth_7_gac_min_entropy,
	&g_depth_8_gac_min_entropy,
	&g_depth_9_gac_min_entropy
};

const int		*g_depth_constr_min_entropy[10] = {
	&g_depth_0_constr_min_entropy,
	&g_depth_1_constr_min_entropy,
	&g_depth_2_constr_min_entropy,
	&g_depth_3_constr_min_entropy,
	&g_depth_4_constr_min_entropy,
	&g_depth_5_constr_min_entropy,
	&g_depth_6_constr_min_entropy,
	&g_depth_7_constr_min_entropy,
	&g_depth_8_constr_min_entropy,
	&g_depth_9_constr_min_entropy
};

const int		*g_depth_lookahead_continue_min_entropy[10] = {
	&g_depth_0_lookahead_continue_min_entropy,
	&g_depth_1_lookahead_continue_min_entropy,
	&g_depth_2_lookahead_continue_min_entropy,
	&g_depth_3_lookahead_continue_min_entropy,
	&g_depth_4_lookahead_continue_min_entropy,
	&g_depth_5_lookahead_continue_min_entropy,
	&g_depth_6_lookahead_continue_min_entropy,
	&g_depth_7_lookahead_continue_min_entropy,
	&g_depth_8_lookahead_continue_min_entropy,
	&g_depth_9_lookahead_continue_min_entropy
};

const int		*g_depth_gac_global_min_entropy[10] = {
	&g_depth_0_gac_global_min_entropy,
	&g_depth_1_gac_global_min_entropy,
	&g_depth_2_gac_global_min_entropy,
	&g_depth_3_gac_global_min_entropy,
	&g_depth_4_gac_global_min_entropy,
	&g_depth_5_gac_global_min_entropy,
	&g_depth_6_gac_global_min_entropy,
	&g_depth_7_gac_global_min_entropy,
	&g_depth_8_gac_global_min_entropy,
	&g_depth_9_gac_global_min_entropy
};

const int		*g_depth_constr_global_min_entropy[10] = {
	&g_depth_0_constr_global_min_entropy,
	&g_depth_1_constr_global_min_entropy,
	&g_depth_2_constr_global_min_entropy,
	&g_depth_3_constr_global_min_entropy,
	&g_depth_4_constr_global_min_entropy,
	&g_depth_5_constr_global_min_entropy,
	&g_depth_6_constr_global_min_entropy,
	&g_depth_7_constr_global_min_entropy,
	&g_depth_8_constr_global_min_entropy,
	&g_depth_9_constr_global_min_entropy
};

const int		*g_depth_lookahead_gac_global_min_entropy[10] = {
	&g_depth_0_lookahead_gac_global_min_entropy,
	&g_depth_1_lookahead_gac_global_min_entropy,
	&g_depth_2_lookahead_gac_global_min_entropy,
	&g_depth_3_lookahead_gac_global_min_entropy,
	&g_depth_4_lookahead_gac_global_min_entropy,
	&g_depth_5_lookahead_gac_global_min_entropy,
	&g_depth_6_lookahead_gac_global_min_entropy,
	&g_depth_7_lookahead_gac_global_min_entropy,
	&g_depth_8_lookahead_gac_global_min_entropy,
	&g_depth_9_lookahead_gac_global_min_entropy
};

const int		*g_depth_lookahead_constr_global_min_entropy[10] = {
	&g_depth_0_lookahead_constr_global_min_entropy,
	&g_depth_1_lookahead_constr_global_min_entropy,
	&g_depth_2_lookahead_constr_global_min_entropy,
	&g_depth_3_lookahead_constr_global_min_entropy,
	&g_depth_4_lookahead_constr_global_min_entropy,
	&g_depth_5_lookahead_constr_global_min_entropy,
	&g_depth_6_lookahead_constr_global_min_entropy,
	&g_depth_7_lookahead_constr_global_min_entropy,
	&g_depth_8_lookahead_constr_global_min_entropy,
	&g_depth_9_lookahead_constr_global_min_entropy
};

const double	*g_depth_lookahead_continue_slope[10] = {
	&g_depth_0_lookahead_continue_slope,
	&g_depth_1_lookahead_continue_slope,
	&g_depth_2_lookahead_continue_slope,
	&g_depth_3_lookahead_continue_slope,
	&g_depth_4_lookahead_continue_slope,
	&g_depth_5_lookahead_continue_slope,
	&g_depth_6_lookahead_continue_slope,
	&g_depth_7_lookahead_continue_slope,
	&g_depth_8_lookahead_continue_slope,
	&g_depth_9_lookahead_continue_slope
};

const double	*g_depth_period_coef_scale[10] = {
	&g_depth_0_period_coef_scale,
	&g_depth_1_period_coef_scale,
	&g_depth_2_period_coef_scale,
	&g_depth_3_period_coef_scale,
	&g_depth_4_period_coef_scale,
	&g_depth_5_period_coef_scale,
	&g_depth_6_period_coef_scale,
	&g_depth_7_period_coef_scale,
	&g_depth_8_period_coef_scale,
	&g_depth_9_period_coef_scale
};

const double	*g_depth_period_coef_unset[10] = {
	&g_depth_0_period_coef_unset,
	&g_depth_1_period_coef_unset,
	&g_depth_2_period_coef_unset,
	&g_depth_3_period_coef_unset,
	&g_depth_4_period_coef_unset,
	&g_depth_5_period_coef_unset,
	&g_depth_6_period_coef_unset,
	&g_depth_7_period_coef_unset,
	&g_depth_8_period_coef_unset,
	&g_depth_9_period_coef_unset
};

const double	*g_depth_period_tier_medium_mult[10] = {
	&g_depth_0_period_tier_medium_mult,
	&g_depth_1_period_tier_medium_mult,
	&g_depth_2_period_tier_medium_mult,
	&g_depth_3_period_tier_medium_mult,
	&g_depth_4_period_tier_medium_mult,
	&g_depth_5_period_tier_medium_mult,
	&g_depth_6_period_tier_medium_mult,
	&g_depth_7_period_tier_medium_mult,
	&g_depth_8_period_tier_medium_mult,
	&g_depth_9_period_tier_medium_mult
};

const double	*g_depth_period_tier_heavy_mult[10] = {
	&g_depth_0_period_tier_heavy_mult,
	&g_depth_1_period_tier_heavy_mult,
	&g_depth_2_period_tier_heavy_mult,
	&g_depth_3_period_tier_heavy_mult,
	&g_depth_4_period_tier_heavy_mult,
	&g_depth_5_period_tier_heavy_mult,
	&g_depth_6_period_tier_heavy_mult,
	&g_depth_7_period_tier_heavy_mult,
	&g_depth_8_period_tier_heavy_mult,
	&g_depth_9_period_tier_heavy_mult
};

const double	*g_depth_gac_local_min_entropy[10] = {
	&g_depth_0_gac_local_min_entropy,
	&g_depth_1_gac_local_min_entropy,
	&g_depth_2_gac_local_min_entropy,
	&g_depth_3_gac_local_min_entropy,
	&g_depth_4_gac_local_min_entropy,
	&g_depth_5_gac_local_min_entropy,
	&g_depth_6_gac_local_min_entropy,
	&g_depth_7_gac_local_min_entropy,
	&g_depth_8_gac_local_min_entropy,
	&g_depth_9_gac_local_min_entropy
};

const double	*g_depth_gac_local_max_entropy[10] = {
	&g_depth_0_gac_local_max_entropy,
	&g_depth_1_gac_local_max_entropy,
	&g_depth_2_gac_local_max_entropy,
	&g_depth_3_gac_local_max_entropy,
	&g_depth_4_gac_local_max_entropy,
	&g_depth_5_gac_local_max_entropy,
	&g_depth_6_gac_local_max_entropy,
	&g_depth_7_gac_local_max_entropy,
	&g_depth_8_gac_local_max_entropy,
	&g_depth_9_gac_local_max_entropy
};

const double	*g_depth_constr_local_min_entropy[10] = {
	&g_depth_0_constr_local_min_entropy,
	&g_depth_1_constr_local_min_entropy,
	&g_depth_2_constr_local_min_entropy,
	&g_depth_3_constr_local_min_entropy,
	&g_depth_4_constr_local_min_entropy,
	&g_depth_5_constr_local_min_entropy,
	&g_depth_6_constr_local_min_entropy,
	&g_depth_7_constr_local_min_entropy,
	&g_depth_8_constr_local_min_entropy,
	&g_depth_9_constr_local_min_entropy
};

const double	*g_depth_constr_local_max_entropy[10] = {
	&g_depth_0_constr_local_max_entropy,
	&g_depth_1_constr_local_max_entropy,
	&g_depth_2_constr_local_max_entropy,
	&g_depth_3_constr_local_max_entropy,
	&g_depth_4_constr_local_max_entropy,
	&g_depth_5_constr_local_max_entropy,
	&g_depth_6_constr_local_max_entropy,
	&g_depth_7_constr_local_max_entropy,
	&g_depth_8_constr_local_max_entropy,
	&g_depth_9_constr_local_max_entropy
};

const double	*g_depth_lookahead_gac_local_min_entropy[10] = {
	&g_depth_0_lookahead_gac_local_min_entropy,
	&g_depth_1_lookahead_gac_local_min_entropy,
	&g_depth_2_lookahead_gac_local_min_entropy,
	&g_depth_3_lookahead_gac_local_min_entropy,
	&g_depth_4_lookahead_gac_local_min_entropy,
	&g_depth_5_lookahead_gac_local_min_entropy,
	&g_depth_6_lookahead_gac_local_min_entropy,
	&g_depth_7_lookahead_gac_local_min_entropy,
	&g_depth_8_lookahead_gac_local_min_entropy,
	&g_depth_9_lookahead_gac_local_min_entropy
};

const double	*g_depth_lookahead_gac_local_max_entropy[10] = {
	&g_depth_0_lookahead_gac_local_max_entropy,
	&g_depth_1_lookahead_gac_local_max_entropy,
	&g_depth_2_lookahead_gac_local_max_entropy,
	&g_depth_3_lookahead_gac_local_max_entropy,
	&g_depth_4_lookahead_gac_local_max_entropy,
	&g_depth_5_lookahead_gac_local_max_entropy,
	&g_depth_6_lookahead_gac_local_max_entropy,
	&g_depth_7_lookahead_gac_local_max_entropy,
	&g_depth_8_lookahead_gac_local_max_entropy,
	&g_depth_9_lookahead_gac_local_max_entropy
};

const double	*g_depth_lookahead_constr_local_min_entropy[10] = {
	&g_depth_0_lookahead_constr_local_min_entropy,
	&g_depth_1_lookahead_constr_local_min_entropy,
	&g_depth_2_lookahead_constr_local_min_entropy,
	&g_depth_3_lookahead_constr_local_min_entropy,
	&g_depth_4_lookahead_constr_local_min_entropy,
	&g_depth_5_lookahead_constr_local_min_entropy,
	&g_depth_6_lookahead_constr_local_min_entropy,
	&g_depth_7_lookahead_constr_local_min_entropy,
	&g_depth_8_lookahead_constr_local_min_entropy,
	&g_depth_9_lookahead_constr_local_min_entropy
};

const double	*g_depth_lookahead_constr_local_max_entropy[10] = {
	&g_depth_0_lookahead_constr_local_max_entropy,
	&g_depth_1_lookahead_constr_local_max_entropy,
	&g_depth_2_lookahead_constr_local_max_entropy,
	&g_depth_3_lookahead_constr_local_max_entropy,
	&g_depth_4_lookahead_constr_local_max_entropy,
	&g_depth_5_lookahead_constr_local_max_entropy,
	&g_depth_6_lookahead_constr_local_max_entropy,
	&g_depth_7_lookahead_constr_local_max_entropy,
	&g_depth_8_lookahead_constr_local_max_entropy,
	&g_depth_9_lookahead_constr_local_max_entropy
};

const double	*g_routing_depth_ratio_le7[9] = {
	&g_routing_depth_0_ratio_le7,
	&g_routing_depth_1_ratio_le7,
	&g_routing_depth_2_ratio_le7,
	&g_routing_depth_3_ratio_le7,
	&g_routing_depth_4_ratio_le7,
	&g_routing_depth_5_ratio_le7,
	&g_routing_depth_6_ratio_le7,
	&g_routing_depth_7_ratio_le7,
	&g_routing_depth_8_ratio_le7
};

const double	*g_routing_depth_ratio_s8[9] = {
	&g_routing_depth_0_ratio_s8,
	&g_routing_depth_1_ratio_s8,
	&g_routing_depth_2_ratio_s8,
	&g_routing_depth_3_ratio_s8,
	&g_routing_depth_4_ratio_s8,
	&g_routing_depth_5_ratio_s8,
	&g_routing_depth_6_ratio_s8,
	&g_routing_depth_7_ratio_s8,
	&g_routing_depth_8_ratio_s8
};

const double	*g_routing_depth_ratio_s9[9] = {
	&g_routing_depth_0_ratio_s9,
	&g_routing_depth_1_ratio_s9,
	&g_routing_depth_2_ratio_s9,
	&g_routing_depth_3_ratio_s9,
	&g_routing_depth_4_ratio_s9,
	&g_routing_depth_5_ratio_s9,
	&g_routing_depth_6_ratio_s9,
	&g_routing_depth_7_ratio_s9,
	&g_routing_depth_8_ratio_s9
};
