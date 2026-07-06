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

int	propagate_single_direction(t_puzzle *puzzle, t_node_state *state, int *grid_indices,
		int size, int target_clue)
{
	int				cell_domains[MAX_SIZE];
	t_dp_tables		dp;
	t_prune_args	args;

	if (!collect_domains(state, grid_indices, size, cell_domains))
		return (0);
	init_dp_tables(&dp, size);
	fill_pref_dp(&dp, cell_domains, size);
	fill_suff_dp(&dp, cell_domains, size);
	args.puzzle = puzzle;
	args.state = state;
	args.dp = &dp;
	args.grid_indices = grid_indices;
	args.size = size;
	args.target_clue = target_clue;
	return (prune_candidates(&args));
}
