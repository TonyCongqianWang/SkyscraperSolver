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
#include "grid_manipulation.h"

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

static int	prune_val(t_prune_args *args, int cell, int i, int v)
{
	if (is_valid_value(args->state, cell, v)
		&& !check_candidate(args, i, v))
	{
		set_value_invalid(args->state, cell, v);
		return (1);
	}
	return (0);
}

int	prune_candidates(t_prune_args *args)
{
	int	i;
	int	v;
	int	cell;
	int	changed;

	changed = 0;
	i = -1;
	while (++i < args->size)
	{
		cell = args->grid_indices[i];
		if (args->state->grid.vals[cell] == 0)
		{
			v = 0;
			while (++v <= args->size)
			{
				if (prune_val(args, cell, i, v))
					changed = 1;
				if (args->state->is_invalid)
					return (changed);
			}
		}
	}
	return (changed);
}
