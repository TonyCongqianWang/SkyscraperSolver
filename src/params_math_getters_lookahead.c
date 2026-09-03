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
#include "params_depth_arrays.h"

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

double	get_routing_depth_ratio(int size, int border_idx)
{
	if (size <= 7)
		return (*g_routing_depth_ratio_le7[border_idx]);
	else if (size == 8)
		return (*g_routing_depth_ratio_s8[border_idx]);
	return (*g_routing_depth_ratio_s9[border_idx]);
}
