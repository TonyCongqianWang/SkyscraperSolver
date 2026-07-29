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

double	g_routing_shallow_ratio = 0.21150434795739578;
double	g_routing_medium_ratio = 0.3498467688222415;
double	g_sel_period_coef_sqrt = 8503.516944948424;
double	g_sel_period_coef_inv = 14696.975829462683;
double	g_root_lookahead_continue_slope = 0.5039206051445734;
double	g_root_period_coef_scale = 97.53720672666628;
double	g_root_period_coef_unset = 0.9726044942656924;
double	g_root_period_tier_medium_mult = 2.272930729303751;
double	g_root_period_tier_heavy_mult = 3.5844896412719014;
double	g_root_gac_local_min_entropy = 0.2622927896719175;
double	g_root_gac_local_max_entropy = 0.899048410400633;
double	g_root_constr_local_min_entropy = 0.24835390292631548;
double	g_root_constr_local_max_entropy = 0.905063337574051;
double	g_root_lookahead_gac_local_min_entropy = 0.24321846959902238;
double	g_root_lookahead_gac_local_max_entropy = 0.8759443480945691;
double	g_root_lookahead_constr_local_min_entropy = 0.26173506722364304;
double	g_root_lookahead_constr_local_max_entropy = 0.9030685531351474;
double	g_shallow_lookahead_continue_slope = 0.513792744501945;
double	g_shallow_period_coef_scale = 101.78531158876207;
double	g_shallow_period_coef_unset = 1.8501547945963588;
double	g_shallow_period_tier_medium_mult = 1.9921890377814995;
double	g_shallow_period_tier_heavy_mult = 4.305349215539216;
double	g_shallow_gac_local_min_entropy = 0.2543229908663242;
double	g_shallow_gac_local_max_entropy = 0.8745601336424232;
double	g_shallow_constr_local_min_entropy = 0.2784872807119506;
double	g_shallow_constr_local_max_entropy = 0.8770743198230011;
double	g_shallow_lookahead_gac_local_min_entropy = 0.2407258056672207;
double	g_shallow_lookahead_gac_local_max_entropy = 0.8453115347692239;
double	g_shallow_lookahead_constr_local_min_entropy = 0.3760807722842696;
double	g_shallow_lookahead_constr_local_max_entropy = 0.9140946092072596;
double	g_medium_lookahead_continue_slope = 0.4885139991449761;
double	g_medium_period_coef_scale = 238.618048719283;
double	g_medium_period_coef_unset = 2.660083536650484;
double	g_medium_period_tier_medium_mult = 2.282225442612793;
double	g_medium_period_tier_heavy_mult = 4.680054221193002;
double	g_medium_gac_local_min_entropy = 0.2516595615523248;
double	g_medium_gac_local_max_entropy = 0.9159728048663168;
double	g_medium_constr_local_min_entropy = 0.25829376540902643;
double	g_medium_constr_local_max_entropy = 0.8512000981549454;
double	g_medium_lookahead_gac_local_min_entropy = 0.2866871783872932;
double	g_medium_lookahead_gac_local_max_entropy = 0.8301708425427254;
double	g_medium_lookahead_constr_local_min_entropy = 0.2682169054456001;
double	g_medium_lookahead_constr_local_max_entropy = 0.879535592286335;
double	g_deep_lookahead_continue_slope = 0.5426170557755694;
double	g_deep_period_coef_scale = 619.3959602432046;
double	g_deep_period_coef_unset = 5.895159659299808;
double	g_deep_period_tier_medium_mult = 1.9638798508056676;
double	g_deep_period_tier_heavy_mult = 3.290697954025376;
double	g_deep_gac_local_min_entropy = 0.2975743006903258;
double	g_deep_gac_local_max_entropy = 0.8431956460221665;
double	g_deep_constr_local_min_entropy = 0.26623419485892325;
double	g_deep_constr_local_max_entropy = 0.8714370395103259;
double	g_deep_lookahead_gac_local_min_entropy = 0.2549729416593854;
double	g_deep_lookahead_gac_local_max_entropy = 0.9453609346827506;
double	g_deep_lookahead_constr_local_min_entropy = 0.256793122046651;
double	g_deep_lookahead_constr_local_max_entropy = 0.8333665661005059;
