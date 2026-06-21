/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 14:02:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_check_constr.h"
#include "pruning_routines.h"
#include "constraint_checking.h"
#include "constraint_selection.h"
#include "cell_bounds.h"
#include "grid_availability.h"
#include "grid_manipulation.h"

static int	propagate_single_direction(t_node_state *state, int *grid_indices,
				int size, int target_clue)
{
	int		cell_domains[MAX_SIZE];
	char	pref_max_vis[MAX_SIZE + 1][MAX_SIZE + 1];
	char	pref_min_vis[MAX_SIZE + 1][MAX_SIZE + 1];
	char	suff_max_vis[MAX_SIZE + 1][MAX_SIZE + 1];
	char	suff_min_vis[MAX_SIZE + 1][MAX_SIZE + 1];
	int		changed;
	int		i;
	int		k;
	int		m;
	int		x;
	int		v;

	changed = 0;
	i = 0;
	while (i < size)
	{
		int cell_idx = grid_indices[i];
		int domain_mask = 0;
		if (state->grid.vals[cell_idx] != 0)
		{
			domain_mask = (1 << (state->grid.vals[cell_idx] - 1));
		}
		else
		{
			v = 1;
			while (v <= size)
			{
				if (is_valid_value(state, cell_idx, v))
					domain_mask |= (1 << (v - 1));
				v++;
			}
		}
		if (domain_mask == 0)
		{
			state->is_invalid = 1;
			return (0);
		}
		cell_domains[i] = domain_mask;
		i++;
	}

	// Prefix DP initialization
	k = 0;
	while (k <= size)
	{
		m = 0;
		while (m <= size)
		{
			pref_max_vis[k][m] = -1;
			pref_min_vis[k][m] = 100;
			m++;
		}
		k++;
	}
	pref_max_vis[0][0] = 0;
	pref_min_vis[0][0] = 0;

	// Fill Prefix DP
	k = 0;
	while (k < size)
	{
		int mask = cell_domains[k];
		m = 0;
		while (m <= size)
		{
			if (pref_max_vis[k][m] != -1)
			{
				int max_v = pref_max_vis[k][m];
				int min_v = pref_min_vis[k][m];

				x = 1;
				while (x <= size)
				{
					if (mask & (1 << (x - 1)))
					{
						if (x > m)
						{
							if (max_v + 1 > pref_max_vis[k + 1][x])
								pref_max_vis[k + 1][x] = max_v + 1;
							if (min_v + 1 < pref_min_vis[k + 1][x])
								pref_min_vis[k + 1][x] = min_v + 1;
						}
						else
						{
							if (max_v > pref_max_vis[k + 1][m])
								pref_max_vis[k + 1][m] = max_v;
							if (min_v < pref_min_vis[k + 1][m])
								pref_min_vis[k + 1][m] = min_v;
						}
					}
					x++;
				}
			}
			m++;
		}
		k++;
	}

	// Suffix DP initialization
	k = 0;
	while (k <= size)
	{
		m = 0;
		while (m <= size)
		{
			suff_max_vis[k][m] = -1;
			suff_min_vis[k][m] = 100;
			m++;
		}
		k++;
	}
	m = 0;
	while (m <= size)
	{
		suff_max_vis[size][m] = 0;
		suff_min_vis[size][m] = 0;
		m++;
	}

	// Fill Suffix DP
	k = size - 1;
	while (k >= 0)
	{
		int mask = cell_domains[k];
		m = 0;
		while (m <= size)
		{
			int current_max = -1;
			int current_min = 100;

			x = 1;
			while (x <= size)
			{
				if (mask & (1 << (x - 1)))
				{
					if (x > m)
					{
						if (suff_max_vis[k + 1][x] != -1)
						{
							int val = 1 + suff_max_vis[k + 1][x];
							if (val > current_max)
								current_max = val;
						}
						if (suff_min_vis[k + 1][x] != 100)
						{
							int val = 1 + suff_min_vis[k + 1][x];
							if (val < current_min)
								current_min = val;
						}
					}
					else
					{
						if (suff_max_vis[k + 1][m] != -1)
						{
							int val = suff_max_vis[k + 1][m];
							if (val > current_max)
								current_max = val;
						}
						if (suff_min_vis[k + 1][m] != 100)
						{
							int val = suff_min_vis[k + 1][m];
							if (val < current_min)
								current_min = val;
						}
					}
				}
				x++;
			}
			suff_max_vis[k][m] = current_max;
			suff_min_vis[k][m] = current_min;
			m++;
		}
		k--;
	}

	// Pruning phase
	i = 0;
	while (i < size)
	{
		int cell_idx = grid_indices[i];
		if (state->grid.vals[cell_idx] == 0)
		{
			v = 1;
			while (v <= size)
			{
				if (is_valid_value(state, cell_idx, v))
				{
					int is_candidate_valid = 0;
					m = 0;
					while (m <= size)
					{
						if (pref_max_vis[i][m] != -1)
						{
							int vis_add = (v > m ? 1 : 0);
							int next_m = (v > m ? v : m);

							if (suff_max_vis[i + 1][next_m] != -1)
							{
								int total_max = pref_max_vis[i][m] + vis_add
									+ suff_max_vis[i + 1][next_m];
								int total_min = pref_min_vis[i][m] + vis_add
									+ suff_min_vis[i + 1][next_m];

								if (total_min <= target_clue
									&& target_clue <= total_max)
								{
									is_candidate_valid = 1;
									break ;
								}
							}
						}
						m++;
					}

					if (!is_candidate_valid)
					{
						set_value_invalid(state, cell_idx, v);
						changed = 1;
						if (state->is_invalid)
							return (changed);
					}
				}
				v++;
			}
		}
		i++;
	}

	return (changed);
}

void	prune_check_constr(t_puzzle *puzzle,
			t_selectivity_level selectivity)
{
	t_node_state	*state;
	int				size;
	int				changed;
	int				iterations;
	int				idx;

	state = puzzle->cur_node;
	size = state->size;
	changed = 1;
	iterations = 0;
	while (changed && !state->is_invalid && iterations++ < 100)
	{
		changed = 0;
		idx = 0;
		while (idx < 2 * size)
		{
			int should_process = 0;
			if (selectivity == SELECTIVITY_NONE)
			{
				should_process = 1;
			}
			else if (idx < size)
			{
				int col = idx;
				if ((state->cols_changed_since_prune & (1 << col))
					|| (selectivity == SELECTIVITY_ANY_CHANGE
						&& (state->cols_invalid_since_prune & (1 << col))))
				{
					should_process = 1;
				}
			}
			else
			{
				int row = idx - size;
				if ((state->rows_changed_since_prune & (1 << row))
					|| (selectivity == SELECTIVITY_ANY_CHANGE
						&& (state->rows_invalid_since_prune & (1 << row))))
				{
					should_process = 1;
				}
			}

			if (should_process)
			{
				int grid_indices[MAX_SIZE];
				int rev_indices[MAX_SIZE];
				int target_clue_fwd;
				int target_clue_bwd;
				int i;

				set_active_constraint(puzzle, idx);
				t_constraint_bounds *bounds = &puzzle->constr_bounds;
				target_clue_fwd = bounds->cur_c_pair.fwd_val;
				target_clue_bwd = bounds->cur_c_pair.bwd_val;
				i = 0;
				while (i < size)
				{
					grid_indices[i] = bounds->cur_c_pair.grid_indeces[i];
					rev_indices[i] = bounds->cur_c_pair.grid_indeces[size - 1 - i];
					i++;
				}

				if (target_clue_fwd != 0)
				{
					int bits_pruned = propagate_single_direction(state,
						grid_indices, size, target_clue_fwd);
					if (bits_pruned)
						changed = 1;
					if (state->is_invalid)
						return ;
				}

				if (target_clue_bwd != 0)
				{
					int bits_pruned = propagate_single_direction(state,
						rev_indices, size, target_clue_bwd);
					if (bits_pruned)
						changed = 1;
					if (state->is_invalid)
						return ;
				}
			}
			idx++;
		}
	}
}
