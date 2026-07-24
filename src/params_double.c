/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_double.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_double.h"

double	g_routing_shallow_ratio = 0.21694617605868;
double	g_routing_medium_ratio = 0.34890330972895;
double	g_sel_period_coef_sqrt = 9007.2492054366;
double	g_sel_period_coef_inv = 15857.773828945;
double	g_global_entropy_unset_bias = 500.0;
double	g_root_lookahead_downgrade_fraction = 0.46294416911457;
double	g_root_period_coef_scale = 4799.2167925152;
double	g_root_period_coef_unset = 1.5987496630714;
double	g_root_period_tier_medium_mult = 2.08455472394677;
double	g_root_period_tier_heavy_mult = 3.8428652185217;
double	g_root_gac_local_min_entropy = 0.26403984714856;
double	g_root_gac_local_max_entropy = 0.86663709380776;
double	g_root_constr_local_min_entropy = 0.25491863241256;
double	g_root_constr_local_max_entropy = 0.91519577820637;
double	g_root_lookahead_gac_local_min_entropy = 0.25039325177129;
double	g_root_lookahead_gac_local_max_entropy = 0.87008838095546;
double	g_root_lookahead_constr_local_min_entropy = 0.23168816964554;
double	g_root_lookahead_constr_local_max_entropy = 0.88465119749469;
double	g_shallow_lookahead_downgrade_fraction = 0.29612090103214;
double	g_shallow_period_coef_scale = 72.467005980998;
double	g_shallow_period_coef_unset = 1.6499213652034;
double	g_shallow_period_tier_medium_mult = 1.97965250860375;
double	g_shallow_period_tier_heavy_mult = 3.82458699867896;
double	g_shallow_gac_local_min_entropy = 0.25127728658671;
double	g_shallow_gac_local_max_entropy = 0.87573416830981;
double	g_shallow_constr_local_min_entropy = 0.26639221323249;
double	g_shallow_constr_local_max_entropy = 0.90501939952603;
double	g_shallow_lookahead_gac_local_min_entropy = 0.23654414722219;
double	g_shallow_lookahead_gac_local_max_entropy = 0.85744667676117;
double	g_shallow_lookahead_constr_local_min_entropy = 0.32295732577842;
double	g_shallow_lookahead_constr_local_max_entropy = 0.90415608054555;
double	g_medium_lookahead_downgrade_fraction = 0.18861364033551;
double	g_medium_period_coef_scale = 66.594298030099;
double	g_medium_period_coef_unset = 1.9123654003116;
double	g_medium_period_tier_medium_mult = 2.09986356762875;
double	g_medium_period_tier_heavy_mult = 4.43353173644043;
double	g_medium_gac_local_min_entropy = 0.24976692813905;
double	g_medium_gac_local_max_entropy = 0.88287424050584;
double	g_medium_constr_local_min_entropy = 0.2551881873664;
double	g_medium_constr_local_max_entropy = 0.85882035966809;
double	g_medium_lookahead_gac_local_min_entropy = 0.24038403719693;
double	g_medium_lookahead_gac_local_max_entropy = 0.86382652178173;
double	g_medium_lookahead_constr_local_min_entropy = 0.25496670174914;
double	g_medium_lookahead_constr_local_max_entropy = 0.8903038845368;
double	g_deep_lookahead_downgrade_fraction = 0.29612;
double	g_deep_period_coef_scale = 4575.6914627005;
double	g_deep_period_coef_unset = 3.3094640267171;
double	g_deep_period_tier_medium_mult = 2.05736212682385;
double	g_deep_period_tier_heavy_mult = 3.48465986993358;
double	g_deep_gac_local_min_entropy = 0.28536484980293;
double	g_deep_gac_local_max_entropy = 0.85827347117974;
double	g_deep_constr_local_min_entropy = 0.26697111246797;
double	g_deep_constr_local_max_entropy = 0.87844874301787;
double	g_deep_lookahead_gac_local_min_entropy = 0.24417626618407;
double	g_deep_lookahead_gac_local_max_entropy = 0.88571409502717;
double	g_deep_lookahead_constr_local_min_entropy = 0.26981273291865;
double	g_deep_lookahead_constr_local_max_entropy = 0.84642514552612;
