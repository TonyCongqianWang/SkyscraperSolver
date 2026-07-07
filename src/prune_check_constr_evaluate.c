/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr_utils.c                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/21 19:15:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 19:15:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_check_constr.h"
#include "grid_availability.h"
#include "grid_interface.h"

static int	get_cell_domain(t_node_state *state, int cell_idx, int size)
{
	int	domain_mask;
	int	v;

	domain_mask = 0;
	if (state->grid.vals[cell_idx] != 0)
		return (1 << (state->grid.vals[cell_idx] - 1));
	v = 1;
	while (v <= size)
	{
		if (is_valid_value(state, cell_idx, v))
			domain_mask |= (1 << (v - 1));
		v++;
	}
	return (domain_mask);
}

int	collect_domains(t_node_state *state, int *grid_indices,
		int size, int *cell_domains)
{
	int	i;
	int	mask;

	i = 0;
	while (i < size)
	{
		mask = get_cell_domain(state, grid_indices[i], size);
		if (mask == 0)
		{
			state->is_invalid = 1;
			return (0);
		}
		cell_domains[i] = mask;
		i++;
	}
	return (1);
}

static int	check_candidate(t_prune_args *args, int i, int v)
{
	int	m;
	int	vis_add;
	int	next_m;

	m = 0;
	while (m <= args->size)
	{
		if (args->dp->pref_max[i][m] != -1)
		{
			vis_add = (v > m);
			next_m = m;
			if (v > m)
				next_m = v;
			if (args->dp->suff_max[i + 1][next_m] != -1
				&& args->dp->pref_min[i][m] + vis_add
				+ args->dp->suff_min[i + 1][next_m] <= args->target_clue
				&& args->target_clue <= args->dp->pref_max[i][m] + vis_add
				+ args->dp->suff_max[i + 1][next_m])
				return (1);
		}
		m++;
	}
	return (0);
}

static void	collect_cell_prunes(t_prune_args *args, int i,
				t_grid_update *updates, int *count)
{
	int	v;
	int	cell;

	cell = args->grid_indices[i];
	v = 1;
	while (v <= args->size)
	{
		if (is_valid_value(args->state, cell, v)
			&& !check_candidate(args, i, v))
		{
			updates[*count].cell_idx = cell;
			updates[*count].val = v;
			(*count)++;
		}
		v++;
	}
}

int	prune_candidates(t_prune_args *args)
{
	t_grid_update	updates[MAX_SIZE * MAX_SIZE];
	int				count;
	int				i;
	int				cell;

	count = 0;
	i = 0;
	while (i < args->size)
	{
		cell = args->grid_indices[i];
		if (args->state->grid.vals[cell] == 0)
			collect_cell_prunes(args, i, updates, &count);
		i++;
	}
	if (count > 0)
	{
		set_cells_invalid_batch(args->puzzle, updates, count, g_check_none);
		return (1);
	}
	return (0);
}
