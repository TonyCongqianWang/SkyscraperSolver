/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_int.h                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_INT_H
# define PARAMS_INT_H

/* Root Tier Int Parameters */
extern int	g_root_min_entropy;
extern int	g_root_gac_min_entropy;
extern int	g_root_constr_min_entropy;
extern int	g_root_gac_global_min_entropy;
extern int	g_root_constr_global_min_entropy;
extern int	g_root_lookahead_gac_global_min_entropy;
extern int	g_root_lookahead_constr_global_min_entropy;

/* Shallow Tier Int Parameters */
extern int	g_shallow_min_entropy;
extern int	g_shallow_gac_min_entropy;
extern int	g_shallow_constr_min_entropy;
extern int	g_shallow_gac_global_min_entropy;
extern int	g_shallow_constr_global_min_entropy;
extern int	g_shallow_lookahead_gac_global_min_entropy;
extern int	g_shallow_lookahead_constr_global_min_entropy;

/* Medium Tier Int Parameters */
extern int	g_medium_min_entropy;
extern int	g_medium_gac_min_entropy;
extern int	g_medium_constr_min_entropy;
extern int	g_medium_gac_global_min_entropy;
extern int	g_medium_constr_global_min_entropy;
extern int	g_medium_lookahead_gac_global_min_entropy;
extern int	g_medium_lookahead_constr_global_min_entropy;

/* Deep Tier Int Parameters */
extern int	g_deep_min_entropy;
extern int	g_deep_gac_min_entropy;
extern int	g_deep_constr_min_entropy;
extern int	g_deep_gac_global_min_entropy;
extern int	g_deep_constr_global_min_entropy;
extern int	g_deep_lookahead_gac_global_min_entropy;
extern int	g_deep_lookahead_constr_global_min_entropy;

#endif
