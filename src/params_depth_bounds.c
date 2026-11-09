/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_depth_bounds.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/05 14:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/10/05 14:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "params_depth_arrays.h"
#include <limits.h>

/* Cubic extrapolation is retained; integer schedules saturate on overflow. */
int	schedule_int(double value)
{
	if (value <= 0.0)
		return (0);
	if (value >= INT_MAX)
		return (INT_MAX);
	return ((int)value);
}
