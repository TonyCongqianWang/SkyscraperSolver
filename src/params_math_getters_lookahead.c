/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math_getters_lookahead.c                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

double	get_lookahead_score_weight_split0(int size)
{
	if (size <= 7)
		return (g_lookahead_score_weight_split0_le7);
	if (size == 8)
		return (g_lookahead_score_weight_split0_s8);
	return (g_lookahead_score_weight_split0_s9);
}

double	get_lookahead_score_weight_split1(int size)
{
	if (size <= 7)
		return (g_lookahead_score_weight_split1_le7);
	if (size == 8)
		return (g_lookahead_score_weight_split1_s8);
	return (g_lookahead_score_weight_split1_s9);
}

double	get_lookahead_entropy_weight(int size)
{
	if (size <= 7)
		return (g_lookahead_entropy_weight_le7);
	if (size == 8)
		return (g_lookahead_entropy_weight_s8);
	return (g_lookahead_entropy_weight_s9);
}
