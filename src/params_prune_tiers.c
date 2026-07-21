/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_prune_tiers.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_prune_tiers.h"

const int	g_root_min_entropy = 70188;
const int	g_root_gac_min_entropy = 62796;
const int	g_root_constr_min_entropy = 74412;
const double	g_root_lookahead_downgrade_fraction = 0.0293464413205669;
const double	g_root_period_coef_sqrt = 2680.26110058258;
const double	g_root_period_coef_inv = 1505.9904959552;
const double	g_root_period_coef_unset = 0.489886558416355;
const double	g_root_period_tier_medium_mult = 2.08455472394677;
const double	g_root_period_tier_heavy_mult = 3.8428652185217;
const int	g_shallow_min_entropy = 129398;
const int	g_shallow_gac_min_entropy = 181264;
const int	g_shallow_constr_min_entropy = 413576;
const double	g_shallow_lookahead_downgrade_fraction = 0.0133404154416888;
const double	g_shallow_period_coef_sqrt = 20.3940309957776;
const double	g_shallow_period_coef_inv = 82.0003588158586;
const double	g_shallow_period_coef_unset = 1.34501947503087;
const double	g_shallow_period_tier_medium_mult = 1.97965250860375;
const double	g_shallow_period_tier_heavy_mult = 3.82458699867896;
const int	g_medium_min_entropy = 241577;
const int	g_medium_gac_min_entropy = 9954;
const int	g_medium_constr_min_entropy = 176710;
const double	g_medium_lookahead_downgrade_fraction = 0.0313312171072548;
const double	g_medium_period_coef_sqrt = 36.3410553162389;
const double	g_medium_period_coef_inv = 11.3227629693435;
const double	g_medium_period_coef_unset = 4.09810076537906;
const double	g_medium_period_tier_medium_mult = 2.09986356762875;
const double	g_medium_period_tier_heavy_mult = 4.43353173644043;
const int	g_deep_min_entropy = 246577;
const int	g_deep_gac_min_entropy = 261334;
const int	g_deep_constr_min_entropy = 514370;
const double	g_deep_lookahead_downgrade_fraction = 0.120374788066341;
const double	g_deep_period_coef_sqrt = 1083.52198515116;
const double	g_deep_period_coef_inv = 2012.79885806126;
const double	g_deep_period_coef_unset = 2.95695576127101;
const double	g_deep_period_tier_medium_mult = 2.05736212682385;
const double	g_deep_period_tier_heavy_mult = 3.48465986993358;
