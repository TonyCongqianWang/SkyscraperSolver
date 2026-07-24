/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_double.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_DOUBLE_H
# define PARAMS_DOUBLE_H

/* Routing Double Parameters */
extern double	g_routing_shallow_ratio;
extern double	g_routing_medium_ratio;
extern double	g_sel_period_coef_sqrt;
extern double	g_sel_period_coef_inv;
extern double	g_global_entropy_unset_bias;

/* Root Tier Double Parameters */
extern double	g_root_lookahead_downgrade_fraction;
extern double	g_root_period_coef_scale;
extern double	g_root_period_coef_unset;
extern double	g_root_period_tier_medium_mult;
extern double	g_root_period_tier_heavy_mult;
extern double	g_root_gac_local_min_entropy;
extern double	g_root_gac_local_max_entropy;
extern double	g_root_constr_local_min_entropy;
extern double	g_root_constr_local_max_entropy;
extern double	g_root_lookahead_gac_local_min_entropy;
extern double	g_root_lookahead_gac_local_max_entropy;
extern double	g_root_lookahead_constr_local_min_entropy;
extern double	g_root_lookahead_constr_local_max_entropy;

/* Shallow Tier Double Parameters */
extern double	g_shallow_lookahead_downgrade_fraction;
extern double	g_shallow_period_coef_scale;
extern double	g_shallow_period_coef_unset;
extern double	g_shallow_period_tier_medium_mult;
extern double	g_shallow_period_tier_heavy_mult;
extern double	g_shallow_gac_local_min_entropy;
extern double	g_shallow_gac_local_max_entropy;
extern double	g_shallow_constr_local_min_entropy;
extern double	g_shallow_constr_local_max_entropy;
extern double	g_shallow_lookahead_gac_local_min_entropy;
extern double	g_shallow_lookahead_gac_local_max_entropy;
extern double	g_shallow_lookahead_constr_local_min_entropy;
extern double	g_shallow_lookahead_constr_local_max_entropy;

/* Medium Tier Double Parameters */
extern double	g_medium_lookahead_downgrade_fraction;
extern double	g_medium_period_coef_scale;
extern double	g_medium_period_coef_unset;
extern double	g_medium_period_tier_medium_mult;
extern double	g_medium_period_tier_heavy_mult;
extern double	g_medium_gac_local_min_entropy;
extern double	g_medium_gac_local_max_entropy;
extern double	g_medium_constr_local_min_entropy;
extern double	g_medium_constr_local_max_entropy;
extern double	g_medium_lookahead_gac_local_min_entropy;
extern double	g_medium_lookahead_gac_local_max_entropy;
extern double	g_medium_lookahead_constr_local_min_entropy;
extern double	g_medium_lookahead_constr_local_max_entropy;

/* Deep Tier Double Parameters */
extern double	g_deep_lookahead_downgrade_fraction;
extern double	g_deep_period_coef_scale;
extern double	g_deep_period_coef_unset;
extern double	g_deep_period_tier_medium_mult;
extern double	g_deep_period_tier_heavy_mult;
extern double	g_deep_gac_local_min_entropy;
extern double	g_deep_gac_local_max_entropy;
extern double	g_deep_constr_local_min_entropy;
extern double	g_deep_constr_local_max_entropy;
extern double	g_deep_lookahead_gac_local_min_entropy;
extern double	g_deep_lookahead_gac_local_max_entropy;
extern double	g_deep_lookahead_constr_local_min_entropy;
extern double	g_deep_lookahead_constr_local_max_entropy;

#endif
