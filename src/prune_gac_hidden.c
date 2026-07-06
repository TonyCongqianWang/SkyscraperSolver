/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac_hidden.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_gac_hidden.h"
#include "prune_gac_domain.h"
#include "grid_availability.h"

static void	check_hidden_pair(t_node_state *state, int *cells, int count,
				int *vals, t_grid_update *updates, int *update_count, int *pruned_masks)
{
	int	u_cells;
	int	i;
	int	keep_mask;

	u_cells = vals[2];
	if (count_bits(u_cells) == 2)
	{
		keep_mask = (1 << vals[0]) | (1 << vals[1]);
		i = 0;
		while (i < count)
		{
			if (u_cells & (1 << i))
				keep_only_values(state, updates, update_count, cells[i], keep_mask, pruned_masks);
			i++;
		}
	}
}

void	analyse_hidden_pairs(t_node_state *state, int *cells, int count,
			int *val_cells, t_grid_update *updates, int *update_count, int *pruned_masks)
{
	int	v1;
	int	v2;
	int	vals[3];

	v1 = -1;
	while (++v1 < state->size)
	{
		v2 = v1;
		while (++v2 < state->size)
		{
			if (val_cells[v1] != 0 && val_cells[v2] != 0)
			{
				vals[0] = v1;
				vals[1] = v2;
				vals[2] = val_cells[v1] | val_cells[v2];
				check_hidden_pair(state, cells, count, vals, updates, update_count, pruned_masks);
			}
		}
	}
}

static void	check_hidden_triple(t_node_state *state, int *cells, int count,
				int *vals, t_grid_update *updates, int *update_count, int *pruned_masks)
{
	int	u_cells;
	int	i;
	int	keep_mask;

	u_cells = vals[3];
	if (count_bits(u_cells) == 3)
	{
		keep_mask = (1 << vals[0]) | (1 << vals[1]) | (1 << vals[2]);
		i = 0;
		while (i < count)
		{
			if (u_cells & (1 << i))
				keep_only_values(state, updates, update_count, cells[i], keep_mask, pruned_masks);
			i++;
		}
	}
}

static void	try_hidden_triple(t_node_state *state, t_hidden_param *p, int *v,
				t_grid_update *updates, int *update_count, int *pruned_masks)
{
	int	vals[4];

	if (p->val_cells[v[0]] != 0 && p->val_cells[v[1]] != 0
		&& p->val_cells[v[2]] != 0)
	{
		vals[0] = v[0];
		vals[1] = v[1];
		vals[2] = v[2];
		vals[3] = p->val_cells[v[0]] | p->val_cells[v[1]]
			| p->val_cells[v[2]];
		check_hidden_triple(state, p->cells, p->count, vals, updates, update_count, pruned_masks);
	}
}

void	analyse_hidden_triples(t_node_state *state, int *cells, int count,
			int *val_cells, t_grid_update *updates, int *update_count, int *pruned_masks)
{
	t_hidden_param	p;
	int				v[3];

	p.cells = cells;
	p.count = count;
	p.val_cells = val_cells;
	v[0] = -1;
	while (++v[0] < state->size)
	{
		v[1] = v[0];
		while (++v[1] < state->size)
		{
			v[2] = v[1];
			while (++v[2] < state->size)
				try_hidden_triple(state, &p, v, updates, update_count, pruned_masks);
		}
	}
}
