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
#include "selectivity.h"
#include "check_node_validity.h"

static int	run_propagate(t_prune_args *args, int clue, int *indices)
{
	if (clue != 0)
	{
		args->grid_indices = indices;
		args->target_clue = clue;
		if (propagate_single_direction(args))
			return (1);
	}
	return (0);
}

int	process_constraint(t_puzzle *puzzle, int idx, int size,
		double min_unset, double max_unset, double global_min_unset)
{
	int				grid_indices[MAX_SIZE];
	int				rev_indices[MAX_SIZE];
	int				clues[2];
	int				changed;
	t_prune_args	args;
	double			global_ratio;
	double			local_ratio;
	int				unset_cnt;
	int				i;

	global_ratio = (double)puzzle->cur_node->num_unset / puzzle->squared_size;
	if (global_ratio < global_min_unset)
		return (0);
	changed = 0;
	set_active_constraint(puzzle, idx);
	clues[0] = puzzle->constr_bounds.cur_c_pair.fwd_val;
	clues[1] = puzzle->constr_bounds.cur_c_pair.bwd_val;
	copy_indices(puzzle, grid_indices, rev_indices, size);
	i = 0;
	unset_cnt = 0;
	while (i < size)
	{
		if (puzzle->cur_node->grid.vals[grid_indices[i]] == 0)
			unset_cnt++;
		i++;
	}
	local_ratio = (double)unset_cnt / size;
	if (local_ratio < min_unset || local_ratio > max_unset)
		return (0);
	args.puzzle = puzzle;
	args.state = puzzle->cur_node;
	args.size = size;
	if (run_propagate(&args, clues[0], grid_indices))
		changed = 1;
	if (puzzle->cur_node->is_invalid)
		return (changed);
	if (run_propagate(&args, clues[1], rev_indices))
		changed = 1;
	return (changed);
}

static int	check_constr_rows(t_puzzle *puzzle, t_node_state *state,
				t_selectivity_level selectivity,
				double min_unset, double max_unset, double global_min_unset)
{
	int	r;
	int	changed;

	changed = 0;
	r = 0;
	while (r < state->size)
	{
		if (should_process_row(state, r, selectivity))
		{
			if (process_constraint(puzzle, r + state->size, state->size,
					min_unset, max_unset, global_min_unset))
				changed = 1;
		}
		r++;
	}
	return (changed);
}

static int	check_constr_cols(t_puzzle *puzzle, t_node_state *state,
				t_selectivity_level selectivity,
				double min_unset, double max_unset, double global_min_unset)
{
	int	c;
	int	changed;

	changed = 0;
	c = 0;
	while (c < state->size)
	{
		if (should_process_col(state, c, selectivity))
		{
			if (process_constraint(puzzle, c, state->size,
					min_unset, max_unset, global_min_unset))
				changed = 1;
		}
		c++;
	}
	return (changed);
}

void	prune_check_constr(t_puzzle *puzzle, t_selectivity_level selectivity,
			double min_unset, double max_unset, double global_min_unset)
{
	t_node_state	*state;
	int				changed;
	int				iterations;

	state = puzzle->cur_node;
	if (should_exit_selectivity(state, selectivity))
		return ;
	changed = 1;
	iterations = 0;
	while (changed && !state->is_invalid && iterations++ < 100)
	{
		changed = 0;
		if (check_constr_cols(puzzle, state, selectivity,
				min_unset, max_unset, global_min_unset))
			changed = 1;
		if (check_constr_rows(puzzle, state, selectivity,
				min_unset, max_unset, global_min_unset))
			changed = 1;
	}
	check_node_validity(puzzle, g_check_constr);
}
