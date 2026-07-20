/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   math_utils.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/20 18:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/20 18:20:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "math_utils.h"

int	isqrt_approx(long long n)
{
	long long	x;
	long long	y;

	if (n <= 1)
		return ((int)n);
	x = n;
	y = (x + 1) / 2;
	while (y < x)
	{
		x = y;
		y = (x + n / x) / 2;
	}
	return ((int)x);
}
