/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_prune_tiers.h                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_PRUNE_TIERS_H
# define PARAMS_PRUNE_TIERS_H

/* Root Tier Parameters */
extern int		g_root_min_entropy;
extern int		g_root_gac_min_entropy;
extern int		g_root_constr_min_entropy;
extern double	g_root_lookahead_downgrade_fraction;
extern double	g_root_period_coef_sqrt;
extern double	g_root_period_coef_inv;
extern double	g_root_period_coef_unset;
extern double	g_root_period_tier_medium_mult;
extern double	g_root_period_tier_heavy_mult;

/* Shallow Tier Parameters */
extern int		g_shallow_min_entropy;
extern int		g_shallow_gac_min_entropy;
extern int		g_shallow_constr_min_entropy;
extern double	g_shallow_lookahead_downgrade_fraction;
extern double	g_shallow_period_coef_sqrt;
extern double	g_shallow_period_coef_inv;
extern double	g_shallow_period_coef_unset;
extern double	g_shallow_period_tier_medium_mult;
extern double	g_shallow_period_tier_heavy_mult;

/* Medium Tier Parameters */
extern int		g_medium_min_entropy;
extern int		g_medium_gac_min_entropy;
extern int		g_medium_constr_min_entropy;
extern double	g_medium_lookahead_downgrade_fraction;
extern double	g_medium_period_coef_sqrt;
extern double	g_medium_period_coef_inv;
extern double	g_medium_period_coef_unset;
extern double	g_medium_period_tier_medium_mult;
extern double	g_medium_period_tier_heavy_mult;

/* Deep Tier Parameters */
extern int		g_deep_min_entropy;
extern int		g_deep_gac_min_entropy;
extern int		g_deep_constr_min_entropy;
extern double	g_deep_lookahead_downgrade_fraction;
extern double	g_deep_period_coef_sqrt;
extern double	g_deep_period_coef_inv;
extern double	g_deep_period_coef_unset;
extern double	g_deep_period_tier_medium_mult;
extern double	g_deep_period_tier_heavy_mult;

#endif
