/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math_getters_lookahead.c                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

double	get_lookahead_score_weight_split0(int size)
{
	if (size <= 7)
		return (g_lookahead_score_weight_split0_le7);
	else if (size == 8)
		return (g_lookahead_score_weight_split0_s8);
	return (g_lookahead_score_weight_split0_s9);
}

double	get_lookahead_score_weight_split1(int size)
{
	if (size <= 7)
		return (g_lookahead_score_weight_split1_le7);
	else if (size == 8)
		return (g_lookahead_score_weight_split1_s8);
	return (g_lookahead_score_weight_split1_s9);
}

double	get_lookahead_entropy_weight(int size)
{
	if (size <= 7)
		return (g_lookahead_entropy_weight_le7);
	else if (size == 8)
		return (g_lookahead_entropy_weight_s8);
	return (g_lookahead_entropy_weight_s9);
}

double	get_depth_warp(int size, int idx)
{
	if (size <= 7 && idx == 0)
		return (g_depth_warp_0_le7);
	if (size <= 7 && idx == 1)
		return (g_depth_warp_1_le7);
	if (size <= 7)
		return (g_depth_warp_2_le7);
	if (size == 8 && idx == 0)
		return (g_depth_warp_0_s8);
	if (size == 8 && idx == 1)
		return (g_depth_warp_1_s8);
	if (size == 8)
		return (g_depth_warp_2_s8);
	if (idx == 0)
		return (g_depth_warp_0_s9);
	if (idx == 1)
		return (g_depth_warp_1_s9);
	return (g_depth_warp_2_s9);
}
