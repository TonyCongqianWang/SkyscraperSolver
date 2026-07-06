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

static void	check_pair(int *cells, int count, int *pair,
				t_gac_batch *batch)
{
	int	u_bmp;
	int	c;

	u_bmp = batch->state->grid.valid_val_bmps[cells[pair[0]]]
		| batch->state->grid.valid_val_bmps[cells[pair[1]]];
	u_bmp &= (1 << batch->state->size) - 1;
	if (count_bits(u_bmp) == 2)
	{
		c = 0;
		while (c < count)
		{
			if (c != pair[0] && c != pair[1])
				eliminate_bmp_vals(batch, cells[c], u_bmp);
			c++;
		}
	}
}

void	analyse_naked_pairs(int *cells, int count, t_gac_batch *batch)
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
			check_pair(cells, count, pair, batch);
			j++;
		}
		i++;
	}
}

static void	check_triple(int *cells, int count,
				int *inds, t_gac_batch *batch)
{
	int	u_bmp;
	int	c;

	u_bmp = batch->state->grid.valid_val_bmps[cells[inds[0]]]
		| batch->state->grid.valid_val_bmps[cells[inds[1]]]
		| batch->state->grid.valid_val_bmps[cells[inds[2]]];
	u_bmp &= (1 << batch->state->size) - 1;
	if (count_bits(u_bmp) == 3)
	{
		c = 0;
		while (c < count)
		{
			if (c != inds[0] && c != inds[1] && c != inds[2])
				eliminate_bmp_vals(batch, cells[c], u_bmp);
			c++;
		}
	}
}

void	analyse_naked_triples(int *cells, int count, t_gac_batch *batch)
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
				check_triple(cells, count, inds, batch);
				l++;
			}
			j++;
		}
		i++;
	}
}
