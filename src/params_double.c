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

double	g_routing_shallow_ratio = 0.20984519385483474;
double	g_routing_medium_ratio = 0.3523645598687041;
double	g_sel_period_coef_sqrt = 8019.054701543802;
double	g_sel_period_coef_inv = 15702.781974174368;
double	g_global_entropy_unset_bias = 516.96;
double	g_global_entropy_unset_bias_s7 = 516.96;
double	g_global_entropy_unset_bias_s8 = 516.96;
double	g_global_entropy_unset_bias_s9 = 516.96;
double	g_root_lookahead_continue_slope = 0.5;
double	g_root_period_coef_scale = 100.0;
double	g_root_period_coef_unset = 1.2322573182625858;
double	g_root_period_tier_medium_mult = 2.272930729303751;
double	g_root_period_tier_heavy_mult = 3.5844896412719014;
double	g_root_gac_local_min_entropy = 0.25973180527123735;
double	g_root_gac_local_max_entropy = 0.874023986239067;
double	g_root_constr_local_min_entropy = 0.26064501261065265;
double	g_root_constr_local_max_entropy = 0.9126105341650526;
double	g_root_lookahead_gac_local_min_entropy = 0.2503278144967727;
double	g_root_lookahead_gac_local_max_entropy = 0.8765735453030373;
double	g_root_lookahead_constr_local_min_entropy = 0.23276766798962922;
double	g_root_lookahead_constr_local_max_entropy = 0.8840393905695386;
double	g_shallow_lookahead_continue_slope = 0.5;
double	g_shallow_period_coef_scale = 100.0;
double	g_shallow_period_coef_unset = 2.1755253971024535;
double	g_shallow_period_tier_medium_mult = 1.9921890377814995;
double	g_shallow_period_tier_heavy_mult = 4.305349215539216;
double	g_shallow_gac_local_min_entropy = 0.24811118930398296;
double	g_shallow_gac_local_max_entropy = 0.8749166261562161;
double	g_shallow_constr_local_min_entropy = 0.25931738796163323;
double	g_shallow_constr_local_max_entropy = 0.8982431059716437;
double	g_shallow_lookahead_gac_local_min_entropy = 0.23288633516328322;
double	g_shallow_lookahead_gac_local_max_entropy = 0.8498986082997585;
double	g_shallow_lookahead_constr_local_min_entropy = 0.3631018758643103;
double	g_shallow_lookahead_constr_local_max_entropy = 0.9038017369503237;
double	g_medium_lookahead_continue_slope = 0.5;
double	g_medium_period_coef_scale = 250.0;
double	g_medium_period_coef_unset = 2.6346616967711145;
double	g_medium_period_tier_medium_mult = 2.282225442612793;
double	g_medium_period_tier_heavy_mult = 4.680054221193002;
double	g_medium_gac_local_min_entropy = 0.24910795309196465;
double	g_medium_gac_local_max_entropy = 0.8769915343370689;
double	g_medium_constr_local_min_entropy = 0.25493120160029764;
double	g_medium_constr_local_max_entropy = 0.8545458587101036;
double	g_medium_lookahead_gac_local_min_entropy = 0.240504752553489;
double	g_medium_lookahead_gac_local_max_entropy = 0.8601715211423747;
double	g_medium_lookahead_constr_local_min_entropy = 0.2560716761364065;
double	g_medium_lookahead_constr_local_max_entropy = 0.8922129640531624;
double	g_deep_lookahead_continue_slope = 0.5;
double	g_deep_period_coef_scale = 600.0;
double	g_deep_period_coef_unset = 5.913134403440602;
double	g_deep_period_tier_medium_mult = 1.9638798508056676;
double	g_deep_period_tier_heavy_mult = 3.290697954025376;
double	g_deep_gac_local_min_entropy = 0.28122234575245253;
double	g_deep_gac_local_max_entropy = 0.8585677707652279;
double	g_deep_constr_local_min_entropy = 0.2659112015907732;
double	g_deep_constr_local_max_entropy = 0.8757376309495251;
double	g_deep_lookahead_gac_local_min_entropy = 0.23993727267459564;
double	g_deep_lookahead_gac_local_max_entropy = 0.8859350540278806;
double	g_deep_lookahead_constr_local_min_entropy = 0.2739735577902606;
double	g_deep_lookahead_constr_local_max_entropy = 0.84858201450305;

double	get_global_entropy_unset_bias(int size)
{
	if (size == 7)
		return (g_global_entropy_unset_bias_s7);
	if (size == 8)
		return (g_global_entropy_unset_bias_s8);
	if (size == 9)
		return (g_global_entropy_unset_bias_s9);
	return (g_global_entropy_unset_bias);
}
