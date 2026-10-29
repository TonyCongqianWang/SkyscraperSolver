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
#include "line_order.h"

static int	do_prop(t_puzzle *puzzle, int *clues, int *grid, int *rev)
{
	t_prune_args	args;
	int				changed;

	changed = 0;
	args.puzzle = puzzle;
	args.state = puzzle->cur_node;
	args.size = puzzle->cur_node->size;
	if (run_propagate(&args, clues[0], grid))
		changed = 1;
	if (puzzle->cur_node->is_invalid)
		return (changed);
	if (run_propagate(&args, clues[1], rev))
		changed = 1;
	return (changed);
}

int	process_constraint(t_puzzle *puzzle, int idx, int size,
		t_constr_limits *limits)
{
	int				grid_indices[MAX_SIZE];
	int				rev_indices[MAX_SIZE];
	int				clues[2];

	set_active_constraint(puzzle, idx);
	clues[0] = puzzle->constr_bounds.cur_c_pair.fwd_val;
	clues[1] = puzzle->constr_bounds.cur_c_pair.bwd_val;
	copy_indices(puzzle, grid_indices, rev_indices, size);
	if (!check_ratios(puzzle, idx, size, limits))
		return (0);
	return (do_prop(puzzle, clues, grid_indices, rev_indices));
}

static int	check_constr_lines(t_puzzle *puzzle, t_node_state *state,
				t_selectivity_level selectivity, t_constr_limits *limits)
{
	t_line_order	*order;
	int				i;
	int				idx;
	int				changed;

	order = get_line_order(state);
	changed = 0;
	i = 0;
	while (i < order->count && !state->is_invalid)
	{
		idx = order->entries[i].constr_idx;
		if (should_process_line(state, idx, selectivity))
		{
			if (process_constraint(puzzle, idx, state->size, limits))
				changed = 1;
		}
		i++;
	}
	return (changed);
}

void	prune_check_constr(t_puzzle *puzzle, t_selectivity_level selectivity,
			t_constr_limits *limits)
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
		changed = check_constr_lines(puzzle, state, selectivity, limits);
	}
	check_node_validity(puzzle, g_check_constr);
}
