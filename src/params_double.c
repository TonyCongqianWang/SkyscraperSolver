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

double	g_routing_shallow_ratio = 0.21543283285366;
double	g_routing_medium_ratio = 0.35318448289589;
double	g_sel_period_coef_sqrt = 8399.6888064977;
double	g_sel_period_coef_inv = 16101.791255324;
double	g_global_entropy_unset_bias = 508.45137330041;
double	g_root_lookahead_downgrade_fraction = 0.4640393155229;
double	g_root_period_coef_scale = 4276.4339979486;
double	g_root_period_coef_unset = 1.5383060194791;
double	g_root_period_tier_medium_mult = 2.08455472394677;
double	g_root_period_tier_heavy_mult = 3.8428652185217;
double	g_root_gac_local_min_entropy = 0.26390497401183;
double	g_root_gac_local_max_entropy = 0.86548160193232;
double	g_root_constr_local_min_entropy = 0.25846778423677;
double	g_root_constr_local_max_entropy = 0.91217992715167;
double	g_root_lookahead_gac_local_min_entropy = 0.24934133186762;
double	g_root_lookahead_gac_local_max_entropy = 0.87224448020925;
double	g_root_lookahead_constr_local_min_entropy = 0.23016113415637;
double	g_root_lookahead_constr_local_max_entropy = 0.88403385377228;
double	g_shallow_lookahead_downgrade_fraction = 0.32976599221386;
double	g_shallow_period_coef_scale = 66.230547304258;
double	g_shallow_period_coef_unset = 2.3132016668599;
double	g_shallow_period_tier_medium_mult = 1.97965250860375;
double	g_shallow_period_tier_heavy_mult = 3.82458699867896;
double	g_shallow_gac_local_min_entropy = 0.25060558708854;
double	g_shallow_gac_local_max_entropy = 0.87542898734012;
double	g_shallow_constr_local_min_entropy = 0.26265937168675;
double	g_shallow_constr_local_max_entropy = 0.90413157438673;
double	g_shallow_lookahead_gac_local_min_entropy = 0.23286261300551;
double	g_shallow_lookahead_gac_local_max_entropy = 0.854832242253;
double	g_shallow_lookahead_constr_local_min_entropy = 0.34528060743962;
double	g_shallow_lookahead_constr_local_max_entropy = 0.90437359051235;
double	g_medium_lookahead_downgrade_fraction = 0.31175615761573;
double	g_medium_period_coef_scale = 152.8612831398;
double	g_medium_period_coef_unset = 1.6151114650914;
double	g_medium_period_tier_medium_mult = 2.09986356762875;
double	g_medium_period_tier_heavy_mult = 4.43353173644043;
double	g_medium_gac_local_min_entropy = 0.24883915887777;
double	g_medium_gac_local_max_entropy = 0.88136843972674;
double	g_medium_constr_local_min_entropy = 0.25337282148409;
double	g_medium_constr_local_max_entropy = 0.85954677571834;
double	g_medium_lookahead_gac_local_min_entropy = 0.23879994972617;
double	g_medium_lookahead_gac_local_max_entropy = 0.86284382249575;
double	g_medium_lookahead_constr_local_min_entropy = 0.25494245103979;
double	g_medium_lookahead_constr_local_max_entropy = 0.89088673888308;
double	g_deep_lookahead_downgrade_fraction = 0.2937463230176;
double	g_deep_period_coef_scale = 4558.2705102122;
double	g_deep_period_coef_unset = 4.0187251585639;
double	g_deep_period_tier_medium_mult = 2.05736212682385;
double	g_deep_period_tier_heavy_mult = 3.48465986993358;
double	g_deep_gac_local_min_entropy = 0.28299649010807;
double	g_deep_gac_local_max_entropy = 0.85478558087985;
double	g_deep_constr_local_min_entropy = 0.26693137573815;
double	g_deep_constr_local_max_entropy = 0.87955952778423;
double	g_deep_lookahead_gac_local_min_entropy = 0.24289738792996;
double	g_deep_lookahead_gac_local_max_entropy = 0.88367006662043;
double	g_deep_lookahead_constr_local_min_entropy = 0.27221770744646;
double	g_deep_lookahead_constr_local_max_entropy = 0.84890826888772;
