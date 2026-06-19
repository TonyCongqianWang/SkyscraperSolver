/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   lookahead_dive.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "lookahead_dive.h"
#include "grid_manipulation.h"
#include "cell_bounds.h"
#include "tree_search.h"
#include "node_selection.h"
#include "constraint_checking.h"
#include "solution_info.h"
#include "node_selection_cache.h"

static int	perform_dive(t_puzzle *puzzle, t_node_transition next, int depth);
static int	check_only_constr(t_puzzle *puzzle, t_node_transition next);

int	do_l_ahead_dive(t_puzzle *puzzle, t_node_transition next, int depth)
{
	if (depth <= 0)
		return (check_only_constr(puzzle, next));
	return (perform_dive(puzzle, next, depth));
}

static int	transition_node(t_puzzle *puzzle, int depth)
{
	int					target_nunset;
	t_node_state		*cur_node;

	cur_node = puzzle->cur_node;
	target_nunset = cur_node->num_unset - depth;
	if (target_nunset <= 0)
		target_nunset = 0;
	cur_node->max_solutions = 1;
	cur_node->target_nunset = target_nunset;
	cur_node->max_depth = cur_node->cur_depth;
	cur_node->max_depth += depth;
	cur_node->sub_node_depth++;
	cur_node->lowest_empty_idx[0] = 0;
	cur_node->lowest_empty_idx[1] = 0;
	cur_node->lowest_empty_idx[2] = 0;
	return (0);
}

static int	perform_dive(t_puzzle *puzzle, t_node_transition next, int depth)
{
	t_sol_info			local_sols;
	t_node_state		old_state;
	t_node_state		*cur_node;
	t_prune_prog		progress;

	cur_node = puzzle->cur_node;
	old_state = *(cur_node);
	transition_node(puzzle, depth);
	local_sols = tree_recursion(puzzle, next);
	progress = cur_node->progress_counter - old_state.progress_counter;
	old_state.lookahead_scores[next.cell_idx][(int)next.cell_val]
		= (double)progress;
	*(cur_node) = old_state;
	sync_cache_stacks(puzzle);
	return (local_sols.solutions_found > 0);
}

static int	check_only_constr(t_puzzle *puzzle, t_node_transition next)
{
	int					is_valid;
	t_node_state		*cur_node;

	cur_node = puzzle->cur_node;
	if (cur_node->grid.vals[next.cell_idx] != 0)
		return (0);
	cur_node->grid.vals[next.cell_idx] = next.cell_val;
	is_valid = check_constraints(puzzle, next.cell_idx);
	cur_node->grid.vals[next.cell_idx] = 0;
	return (is_valid);
}
