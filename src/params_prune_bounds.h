/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_prune_bounds.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_PRUNE_BOUNDS_H
# define PARAMS_PRUNE_BOUNDS_H

/* Root Bounds Parameters */
extern double	g_root_gac_local_min_entropy;
extern double	g_root_gac_local_max_entropy;
extern int		g_root_gac_global_min_entropy;
extern double	g_root_constr_local_min_entropy;
extern double	g_root_constr_local_max_entropy;
extern int		g_root_constr_global_min_entropy;
extern double	g_root_lookahead_gac_local_min_entropy;
extern double	g_root_lookahead_gac_local_max_entropy;
extern int		g_root_lookahead_gac_global_min_entropy;
extern double	g_root_lookahead_constr_local_min_entropy;
extern double	g_root_lookahead_constr_local_max_entropy;
extern int		g_root_lookahead_constr_global_min_entropy;

/* Shallow Bounds Parameters */
extern double	g_shallow_gac_local_min_entropy;
extern double	g_shallow_gac_local_max_entropy;
extern int		g_shallow_gac_global_min_entropy;
extern double	g_shallow_constr_local_min_entropy;
extern double	g_shallow_constr_local_max_entropy;
extern int		g_shallow_constr_global_min_entropy;
extern double	g_shallow_lookahead_gac_local_min_entropy;
extern double	g_shallow_lookahead_gac_local_max_entropy;
extern int		g_shallow_lookahead_gac_global_min_entropy;
extern double	g_shallow_lookahead_constr_local_min_entropy;
extern double	g_shallow_lookahead_constr_local_max_entropy;
extern int		g_shallow_lookahead_constr_global_min_entropy;

/* Medium Bounds Parameters */
extern double	g_medium_gac_local_min_entropy;
extern double	g_medium_gac_local_max_entropy;
extern int		g_medium_gac_global_min_entropy;
extern double	g_medium_constr_local_min_entropy;
extern double	g_medium_constr_local_max_entropy;
extern int		g_medium_constr_global_min_entropy;
extern double	g_medium_lookahead_gac_local_min_entropy;
extern double	g_medium_lookahead_gac_local_max_entropy;
extern int		g_medium_lookahead_gac_global_min_entropy;
extern double	g_medium_lookahead_constr_local_min_entropy;
extern double	g_medium_lookahead_constr_local_max_entropy;
extern int		g_medium_lookahead_constr_global_min_entropy;

/* Deep Bounds Parameters */
extern double	g_deep_gac_local_min_entropy;
extern double	g_deep_gac_local_max_entropy;
extern int		g_deep_gac_global_min_entropy;
extern double	g_deep_constr_local_min_entropy;
extern double	g_deep_constr_local_max_entropy;
extern int		g_deep_constr_global_min_entropy;
extern double	g_deep_lookahead_gac_local_min_entropy;
extern double	g_deep_lookahead_gac_local_max_entropy;
extern int		g_deep_lookahead_gac_global_min_entropy;
extern double	g_deep_lookahead_constr_local_min_entropy;
extern double	g_deep_lookahead_constr_local_max_entropy;
extern int		g_deep_lookahead_constr_global_min_entropy;

#endif
