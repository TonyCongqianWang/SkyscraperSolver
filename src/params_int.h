/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_int.h                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_INT_H
# define PARAMS_INT_H

extern int	g_root_min_entropy;
extern int	g_root_gac_min_entropy;
extern int	g_root_constr_min_entropy;
extern int	g_root_lookahead_continue_min_entropy;
extern int	g_root_gac_global_min_entropy;
extern int	g_root_constr_global_min_entropy;
extern int	g_root_lookahead_gac_global_min_entropy;
extern int	g_root_lookahead_constr_global_min_entropy;

extern int	g_min_entropy_p00;
extern int	g_min_entropy_p25;
extern int	g_min_entropy_p50;
extern int	g_min_entropy_p100;

extern int	g_gac_min_entropy_p00;
extern int	g_gac_min_entropy_p25;
extern int	g_gac_min_entropy_p50;
extern int	g_gac_min_entropy_p100;

extern int	g_constr_min_entropy_p00;
extern int	g_constr_min_entropy_p25;
extern int	g_constr_min_entropy_p50;
extern int	g_constr_min_entropy_p100;

extern int	g_lookahead_continue_min_entropy_p00;
extern int	g_lookahead_continue_min_entropy_p25;
extern int	g_lookahead_continue_min_entropy_p50;
extern int	g_lookahead_continue_min_entropy_p100;

extern int	g_gac_global_min_entropy_p00;
extern int	g_gac_global_min_entropy_p25;
extern int	g_gac_global_min_entropy_p50;
extern int	g_gac_global_min_entropy_p100;

extern int	g_constr_global_min_entropy_p00;
extern int	g_constr_global_min_entropy_p25;
extern int	g_constr_global_min_entropy_p50;
extern int	g_constr_global_min_entropy_p100;

extern int	g_lookahead_gac_global_min_entropy_p00;
extern int	g_lookahead_gac_global_min_entropy_p25;
extern int	g_lookahead_gac_global_min_entropy_p50;
extern int	g_lookahead_gac_global_min_entropy_p100;

extern int	g_lookahead_constr_global_min_entropy_p00;
extern int	g_lookahead_constr_global_min_entropy_p25;
extern int	g_lookahead_constr_global_min_entropy_p50;
extern int	g_lookahead_constr_global_min_entropy_p100;

#endif
