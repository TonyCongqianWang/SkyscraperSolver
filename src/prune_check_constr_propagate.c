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

int	check_ratios(t_puzzle *puzzle, int *grid_indices, int size,
		t_constr_limits *limits)
{
	int		unset_cnt;
	int		i;
	double	local_ratio;

	if ((double)puzzle->cur_node->num_unset / puzzle->squared_size
		< limits->global_min_unset)
		return (0);
	unset_cnt = 0;
	i = 0;
	while (i < size)
	{
		if (puzzle->cur_node->grid.vals[grid_indices[i]] == 0)
			unset_cnt++;
		i++;
	}
	local_ratio = (double)unset_cnt / size;
	return (local_ratio >= limits->min_unset
		&& local_ratio <= limits->max_unset);
}

int	run_propagate(t_prune_args *args, int clue, int *indices)
{
	if (clue != 0)
	{
		args->grid_indices = indices;
		args->target_clue = clue;
		if (propagate_single_direction(args))
			return (1);
	}
	return (0);
}
