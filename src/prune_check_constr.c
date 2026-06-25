/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/21 19:15:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_check_constr.h"
#include "constraint_selection.h"

static void	copy_indices(t_puzzle *puzzle, int *grid, int *rev, int size)
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

int	propagate_single_direction(t_node_state *state, int *grid_indices,
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
	args.state = state;
	args.dp = &dp;
	args.grid_indices = grid_indices;
	args.size = size;
	args.target_clue = target_clue;
	return (prune_candidates(&args));
}

static int	should_process_idx(t_node_state *state, int idx, int size,
				t_selectivity_level selectivity)
{
	int	col;
	int	row;

	if (selectivity == SELECTIVITY_NONE)
		return (1);
	if (idx < size)
	{
		col = idx;
		if ((state->cols_changed_since_prune & (1 << col))
			|| (selectivity == SELECTIVITY_ANY_CHANGE
				&& (state->cols_invalid_since_prune & (1 << col))))
			return (1);
	}
	row = idx - size;
	if (idx >= size && ((state->rows_changed_since_prune & (1 << row))
			|| (selectivity == SELECTIVITY_ANY_CHANGE
				&& (state->rows_invalid_since_prune & (1 << row)))))
		return (1);
	return (0);
}

static int	process_constraint(t_puzzle *puzzle, int idx, int size)
{
	int	grid_indices[MAX_SIZE];
	int	rev_indices[MAX_SIZE];
	int	clues[2];
	int	changed;

	changed = 0;
	set_active_constraint(puzzle, idx);
	clues[0] = puzzle->constr_bounds.cur_c_pair.fwd_val;
	clues[1] = puzzle->constr_bounds.cur_c_pair.bwd_val;
	copy_indices(puzzle, grid_indices, rev_indices, size);
	if (clues[0] != 0 && propagate_single_direction(puzzle->cur_node,
			grid_indices, size, clues[0]))
		changed = 1;
	if (puzzle->cur_node->is_invalid)
		return (changed);
	if (clues[1] != 0 && propagate_single_direction(puzzle->cur_node,
			rev_indices, size, clues[1]))
		changed = 1;
	return (changed);
}

void	prune_check_constr(t_puzzle *puzzle, t_selectivity_level selectivity)
{
	t_node_state	*state;
	int				changed;
	int				iterations;
	int				idx;

	state = puzzle->cur_node;
	changed = 1;
	iterations = 0;
	while (changed && !state->is_invalid && iterations++ < 100)
	{
		changed = 0;
		idx = 0;
		while (idx < 2 * state->size)
		{
			if (should_process_idx(state, idx, state->size, selectivity))
			{
				if (process_constraint(puzzle, idx, state->size))
					changed = 1;
			}
			idx++;
		}
	}
}
