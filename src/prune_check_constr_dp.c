/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr_dp.c                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/21 19:15:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 19:15:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_check_constr.h"

void	init_dp_tables(t_dp_tables *dp, int size)
{
	int	k;
	int	m;

	k = -1;
	while (++k <= size)
	{
		m = -1;
		while (++m <= size)
		{
			dp->pref_max[k][m] = -1;
			dp->pref_min[k][m] = 100;
			dp->suff_max[k][m] = -1;
			dp->suff_min[k][m] = 100;
		}
	}
	dp->pref_max[0][0] = 0;
	dp->pref_min[0][0] = 0;
	m = -1;
	while (++m <= size)
	{
		dp->suff_max[size][m] = 0;
		dp->suff_min[size][m] = 0;
	}
}

static void	update_pref_cell(t_dp_tables *dp, int k, int m, int x)
{
	int	max_v;
	int	min_v;

	max_v = dp->pref_max[k][m];
	min_v = dp->pref_min[k][m];
	if (x > m)
	{
		if (max_v + 1 > dp->pref_max[k + 1][x])
			dp->pref_max[k + 1][x] = max_v + 1;
		if (min_v + 1 < dp->pref_min[k + 1][x])
			dp->pref_min[k + 1][x] = min_v + 1;
	}
	else
	{
		if (max_v > dp->pref_max[k + 1][m])
			dp->pref_max[k + 1][m] = max_v;
		if (min_v < dp->pref_min[k + 1][m])
			dp->pref_min[k + 1][m] = min_v;
	}
}

void	fill_pref_dp(t_dp_tables *dp, int *cell_domains, int size)
{
	int	k;
	int	m;
	int	x;

	k = 0;
	while (k < size)
	{
		m = 0;
		while (m <= size)
		{
			if (dp->pref_max[k][m] != -1)
			{
				x = 1;
				while (x <= size)
				{
					if (cell_domains[k] & (1 << (x - 1)))
						update_pref_cell(dp, k, m, x);
					x++;
				}
			}
			m++;
		}
		k++;
	}
}

static void	update_suff_cell(t_dp_tables *dp, int k, int m, int x)
{
	if (x > m)
	{
		if (dp->suff_max[k + 1][x] != -1
			&& 1 + dp->suff_max[k + 1][x] > dp->suff_max[k][m])
			dp->suff_max[k][m] = 1 + dp->suff_max[k + 1][x];
		if (dp->suff_min[k + 1][x] != 100
			&& 1 + dp->suff_min[k + 1][x] < dp->suff_min[k][m])
			dp->suff_min[k][m] = 1 + dp->suff_min[k + 1][x];
	}
	else
	{
		if (dp->suff_max[k + 1][m] != -1
			&& dp->suff_max[k + 1][m] > dp->suff_max[k][m])
			dp->suff_max[k][m] = dp->suff_max[k + 1][m];
		if (dp->suff_min[k + 1][m] != 100
			&& dp->suff_min[k + 1][m] < dp->suff_min[k][m])
			dp->suff_min[k][m] = dp->suff_min[k + 1][m];
	}
}

void	fill_suff_dp(t_dp_tables *dp, int *cell_domains, int size)
{
	int	k;
	int	m;
	int	x;

	k = size - 1;
	while (k >= 0)
	{
		m = 0;
		while (m <= size)
		{
			dp->suff_max[k][m] = -1;
			dp->suff_min[k][m] = 100;
			x = 1;
			while (x <= size)
			{
				if (cell_domains[k] & (1 << (x - 1)))
					update_suff_cell(dp, k, m, x);
				x++;
			}
			m++;
		}
		k--;
	}
}
