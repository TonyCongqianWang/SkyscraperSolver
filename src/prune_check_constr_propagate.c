/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr_propagate.c                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/26 13:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_check_constr.h"

void	copy_indices(t_puzzle *puzzle, int *grid, int *rev, int size)
{
	int	i;

	i = 0;
	while (i < size)
	{
		grid[i] = puzzle->constr_bounds.cur_c_pair.grid_indeces[i];
		rev[i] = puzzle->constr_bounds.cur_c_pair.grid_indeces[size - 1 - i];
		i++;
	}
}

int	propagate_single_direction(t_prune_args *args)
{
	int			cell_domains[MAX_SIZE];
	t_dp_tables	dp;

	if (!collect_domains(args->state, args->grid_indices, args->size,
			cell_domains))
		return (0);
	init_dp_tables(&dp, args->size);
	fill_pref_dp(&dp, cell_domains, args->size);
	fill_suff_dp(&dp, cell_domains, args->size);
	args->dp = &dp;
	return (prune_candidates(args));
}
