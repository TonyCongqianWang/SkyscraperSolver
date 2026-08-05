/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math_getters_age.c                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/05 23:09:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/05 23:09:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_math.h"

double	get_lookahead_score_age_limit_ratio(int size)
{
	if (size <= 7)
		return (g_lookahead_score_age_limit_ratio_le7);
	if (size == 8)
		return (g_lookahead_score_age_limit_ratio_s8);
	return (g_lookahead_score_age_limit_ratio_s9);
}
