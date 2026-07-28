/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   entropy_weights.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/28 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/28 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "entropy.h"
#include "params_int.h"

int	get_weight_cell(int size)
{
	long long	prod;

	prod = 1000LL * get_weight_cell_constr_ratio_fp(size)
		* get_weight_total_scale_fp(size);
	return ((int)(prod >> 21));
}

int	get_weight_constr(int size)
{
	long long	prod;

	prod = 1000LL * get_weight_total_scale_fp(size);
	return ((int)(prod >> 10));
}
