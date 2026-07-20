/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   entropy_delta.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/20 18:20:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/20 18:20:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "entropy.h"

int	entropy_delta_cell(int old_count)
{
	return ((g_log2_table[old_count] - g_log2_table[old_count - 1])
		* g_weight_cell / ENTROPY_SCALE);
}

int	entropy_delta_constr(int old_count)
{
	return ((g_log2_table[old_count] - g_log2_table[old_count - 1])
		* g_weight_constr / ENTROPY_SCALE);
}
