/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_depth_arrays.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/03 14:30:00 by towang            #+#    #+#             */
/*   Updated: 2026/09/03 14:30:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_DEPTH_ARRAYS_H
# define PARAMS_DEPTH_ARRAYS_H

extern const int	*g_depth_min_entropy[10];
extern const int	*g_depth_gac_min_entropy[10];
extern const int	*g_depth_constr_min_entropy[10];
extern const int	*g_depth_lookahead_continue_min_entropy[10];
extern const int	*g_depth_gac_global_min_entropy[10];
extern const int	*g_depth_constr_global_min_entropy[10];
extern const int	*g_depth_lookahead_gac_global_min_entropy[10];
extern const int	*g_depth_lookahead_constr_global_min_entropy[10];

extern const double	*g_depth_lookahead_continue_slope[10];
extern const double	*g_depth_period_coef_scale[10];
extern const double	*g_depth_period_coef_unset[10];
extern const double	*g_depth_period_tier_medium_mult[10];
extern const double	*g_depth_period_tier_heavy_mult[10];
extern const double	*g_depth_gac_local_min_entropy[10];
extern const double	*g_depth_gac_local_max_entropy[10];
extern const double	*g_depth_constr_local_min_entropy[10];
extern const double	*g_depth_constr_local_max_entropy[10];
extern const double	*g_depth_lookahead_gac_local_min_entropy[10];
extern const double	*g_depth_lookahead_gac_local_max_entropy[10];
extern const double	*g_depth_lookahead_constr_local_min_entropy[10];
extern const double	*g_depth_lookahead_constr_local_max_entropy[10];

extern const double	*g_routing_depth_ratio_le7[9];
extern const double	*g_routing_depth_ratio_s8[9];
extern const double	*g_routing_depth_ratio_s9[9];

#endif
