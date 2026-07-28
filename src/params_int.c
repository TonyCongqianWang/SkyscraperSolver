/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_int.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/22 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/22 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_int.h"

int	g_weight_cell_constr_ratio_fp = 4441;
int	g_weight_cell_constr_ratio_fp_s7 = 4441;
int	g_weight_cell_constr_ratio_fp_s8 = 4441;
int	g_weight_cell_constr_ratio_fp_s9 = 4441;

int	g_weight_total_scale_fp = 1135;
int	g_weight_total_scale_fp_s7 = 1135;
int	g_weight_total_scale_fp_s8 = 1135;
int	g_weight_total_scale_fp_s9 = 1135;

int	get_weight_cell_constr_ratio_fp(int size)
{
	if (size == 7)
		return (g_weight_cell_constr_ratio_fp_s7);
	if (size == 8)
		return (g_weight_cell_constr_ratio_fp_s8);
	if (size == 9)
		return (g_weight_cell_constr_ratio_fp_s9);
	return (g_weight_cell_constr_ratio_fp);
}

int	get_weight_total_scale_fp(int size)
{
	if (size == 7)
		return (g_weight_total_scale_fp_s7);
	if (size == 8)
		return (g_weight_total_scale_fp_s8);
	if (size == 9)
		return (g_weight_total_scale_fp_s9);
	return (g_weight_total_scale_fp);
}
int	g_root_min_entropy = 75388;
int	g_root_gac_min_entropy = 195117;
int	g_root_constr_min_entropy = 59676;
int	g_root_gac_global_min_entropy = 534208;
int	g_root_constr_global_min_entropy = 551339;
int	g_root_lookahead_gac_global_min_entropy = 616350;
int	g_root_lookahead_constr_global_min_entropy = 496734;
int	g_root_lookahead_continue_min_entropy = 80000;
int	g_shallow_min_entropy = 199274;
int	g_shallow_gac_min_entropy = 191845;
int	g_shallow_constr_min_entropy = 402207;
int	g_shallow_gac_global_min_entropy = 650046;
int	g_shallow_constr_global_min_entropy = 475872;
int	g_shallow_lookahead_gac_global_min_entropy = 759767;
int	g_shallow_lookahead_constr_global_min_entropy = 467044;
int	g_shallow_lookahead_continue_min_entropy = 180000;
int	g_medium_min_entropy = 234104;
int	g_medium_gac_min_entropy = 12148;
int	g_medium_constr_min_entropy = 146448;
int	g_medium_gac_global_min_entropy = 549305;
int	g_medium_constr_global_min_entropy = 255546;
int	g_medium_lookahead_gac_global_min_entropy = 523920;
int	g_medium_lookahead_constr_global_min_entropy = 551478;
int	g_medium_lookahead_continue_min_entropy = 200000;
int	g_deep_min_entropy = 264448;
int	g_deep_gac_min_entropy = 266083;
int	g_deep_constr_min_entropy = 483717;
int	g_deep_gac_global_min_entropy = 510812;
int	g_deep_constr_global_min_entropy = 450839;
int	g_deep_lookahead_gac_global_min_entropy = 399383;
int	g_deep_lookahead_constr_global_min_entropy = 494737;
int	g_deep_lookahead_continue_min_entropy = 240000;
