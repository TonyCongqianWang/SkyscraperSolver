/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac_naked.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_gac_naked.h"
#include "prune_gac_domain.h"

static void	check_pair(t_node_state *state, int *cells, int count, int *pair)
{
	int	u_bmp;
	int	c;

	u_bmp = state->grid.valid_val_bmps[cells[pair[0]]]
		| state->grid.valid_val_bmps[cells[pair[1]]];
	if (count_bits(u_bmp) == 2)
	{
		c = 0;
		while (c < count)
		{
			if (c != pair[0] && c != pair[1])
				eliminate_bmp_vals(state, cells[c], u_bmp);
			c++;
		}
	}
}

void	analyse_naked_pairs(t_node_state *state, int *cells, int count)
{
	int	i;
	int	j;
	int	pair[2];

	i = 0;
	while (i < count)
	{
		j = i + 1;
		while (j < count)
		{
			pair[0] = i;
			pair[1] = j;
			check_pair(state, cells, count, pair);
			j++;
		}
		i++;
	}
}

static void	check_triple(t_node_state *state, int *cells, int count,
				int *inds)
{
	int	u_bmp;
	int	c;

	u_bmp = state->grid.valid_val_bmps[cells[inds[0]]]
		| state->grid.valid_val_bmps[cells[inds[1]]]
		| state->grid.valid_val_bmps[cells[inds[2]]];
	if (count_bits(u_bmp) == 3)
	{
		c = 0;
		while (c < count)
		{
			if (c != inds[0] && c != inds[1] && c != inds[2])
				eliminate_bmp_vals(state, cells[c], u_bmp);
			c++;
		}
	}
}

void	analyse_naked_triples(t_node_state *state, int *cells, int count)
{
	int	i;
	int	j;
	int	l;
	int	inds[3];

	i = 0;
	while (i < count)
	{
		j = i + 1;
		while (j < count)
		{
			l = j + 1;
			while (l < count)
			{
				inds[0] = i;
				inds[1] = j;
				inds[2] = l;
				check_triple(state, cells, count, inds);
				l++;
			}
			j++;
		}
		i++;
	}
}
