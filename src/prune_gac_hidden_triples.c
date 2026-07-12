/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac_hidden_triples.c                         :+:      :+:    :+:   */
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

static void	check_hidden_triple(t_hidden_param *p, int *vals,
				t_gac_batch *batch)
{
	int	u_cells;
	int	i;
	int	keep_mask;

	u_cells = vals[3];
	if (count_bits(u_cells) == 3)
	{
		keep_mask = (1 << vals[0]) | (1 << vals[1]) | (1 << vals[2]);
		i = 0;
		while (i < p->count)
		{
			if (u_cells & (1 << i))
				keep_only_values(batch, p->cells[i], keep_mask);
			i++;
		}
	}
}

static void	try_hidden_triple(t_hidden_param *p, int *v, t_gac_batch *batch)
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
		check_hidden_triple(p, vals, batch);
	}
}

void	analyse_hidden_triples(t_node_state *state, t_hidden_param *p,
			t_gac_batch *batch)
{
	int	v[3];

	(void)state;
	v[0] = -1;
	while (++v[0] < state->size)
	{
		v[1] = v[0];
		while (++v[1] < state->size)
		{
			v[2] = v[1];
			while (++v[2] < state->size)
				try_hidden_triple(p, v, batch);
		}
	}
}
