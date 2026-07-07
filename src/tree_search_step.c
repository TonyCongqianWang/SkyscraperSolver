/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   tree_search_step.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "tree_search.h"
#include "grid_interface.h"
#include "strategy_routing.h"
#include "node_selection.h"
#include "solution_info.h"
#include "node_selection_cache.h"

void	backtrack_to_parent(t_puzzle *puzzle, int *d,
			t_search_frame *frames)
{
	t_sol_info	rec_sols;

	rec_sols = frames[*d].node_sols;
	(*d)--;
	puzzle->node_stack_top = *d;
	puzzle->cur_node = &puzzle->node_stack[*d];
	sync_cache_stacks(puzzle);
	if (update_sol_info(&rec_sols, &frames[*d].node_sols)
		|| !check_sol_target(&frames[*d].node_sols, puzzle->cur_node)
		|| rec_sols.min_nunset == puzzle->squared_size)
	{
		set_cell_invalid(puzzle, frames[*d].next.cell_idx,
			frames[*d].next.cell_val, g_check_constr);
	}
}

void	descend_to_child(t_puzzle *puzzle, int *d,
			t_search_frame *frames)
{
	update_sol_target(&frames[*d].node_sols, puzzle->cur_node);
	(*d)++;
	puzzle->node_stack_top = *d;
	puzzle->node_stack[*d] = puzzle->node_stack[*d - 1];
	puzzle->cur_node = &puzzle->node_stack[*d];
	set_cell_val(puzzle, frames[*d - 1].next.cell_idx,
		frames[*d - 1].next.cell_val, g_check_constr);
	puzzle->cur_node->cur_depth++;
	puzzle->nodes_visited++;
	if (puzzle->cur_node->sub_node_depth == 0)
		puzzle->main_nodes_visited++;
}

t_search_result	check_backtrack(t_puzzle *puzzle, int *d, int start_d,
		t_search_frame *frames)
{
	if (*d == start_d)
		return (SEARCH_TERMINATE);
	backtrack_to_parent(puzzle, d, frames);
	return (SEARCH_CONTINUE);
}

static t_search_result	check_early_states(t_puzzle *puzzle, int *d,
							int start_d, t_search_frame *frames)
{
	t_sol_info	rec_sols;
	int			pruned;

	if (check_sol_target(&frames[*d].node_sols, puzzle->cur_node))
		return (check_backtrack(puzzle, d, start_d, frames));
	pruned = prune_current_step(puzzle);
	if (has_reached_terminal_state(puzzle->cur_node))
	{
		rec_sols = handle_leaf_node(puzzle);
		update_sol_info(&rec_sols, &frames[*d].node_sols);
		return (check_backtrack(puzzle, d, start_d, frames));
	}
	if (pruned)
		return (SEARCH_CONTINUE);
	return (SEARCH_PROCEED_TO_BRANCH);
}

t_search_result	process_frame(t_puzzle *puzzle, int *d, int start_d,
		t_search_frame *frames)
{
	t_search_result	early_res;

	early_res = check_early_states(puzzle, d, start_d, frames);
	if (early_res != SEARCH_PROCEED_TO_BRANCH)
		return (early_res);
	init_node_transition(&frames[*d].next);
	if (!try_get_best_transition(puzzle, &frames[*d].next))
		return (check_backtrack(puzzle, d, start_d, frames));
	descend_to_child(puzzle, d, frames);
	if (has_reached_terminal_state(puzzle->cur_node))
	{
		frames[*d].node_sols = handle_leaf_node(puzzle);
		backtrack_to_parent(puzzle, d, frames);
	}
	else
	{
		init_sol_info(&frames[*d].node_sols, puzzle->squared_size, 0);
	}
	return (SEARCH_CONTINUE);
}
