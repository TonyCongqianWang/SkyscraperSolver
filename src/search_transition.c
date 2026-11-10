/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_transition.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "search_context.h"
#include "lookahead_marks.h"
#include "solution_storage.h"
#include "grid_interface.h"
#include "node_selection_transition.h"

void	apply_search_transition(t_solver_state *puzzle, t_node_transition next,
			t_check_mode mode, int is_neg)
{
	rollback_provisional_solution(puzzle);
	puzzle->cur_node->tree.depth++;
	if (puzzle->cur_node->tree.lookahead_depth == 0)
		puzzle->cur_node->tree.unbounded_depth = puzzle->cur_node->tree.depth;
	if (is_neg)
		set_cell_invalid(puzzle, next.cell_idx, next.cell_val, mode);
	else
	{
		mark_lookahead_assignment(puzzle->cur_node->lookahead_ctx, next);
		set_cell_val(puzzle, next.cell_idx, next.cell_val, mode);
	}
}

void	enter_search_child(t_solver_state *puzzle, t_node_transition next,
			t_sol_count solutions_found)
{
	t_node_state	*node;
	int				d;

	d = ++puzzle->node_stack_top;
	puzzle->node_stack[d] = puzzle->node_stack[d - 1];
	puzzle->cur_node = &puzzle->node_stack[d];
	node = puzzle->cur_node;
	if (node->search_policy.limits.max_solutions > 0)
		node->search_policy.limits.max_solutions -= solutions_found;
	apply_search_transition(puzzle, next, g_check_constr, 0);
	puzzle->nodes_visited++;
	if (node->tree.lookahead_depth == 0)
		puzzle->main_nodes_visited++;
}

void	leave_search_child(t_solver_state *puzzle)
{
	puzzle->node_stack_top--;
	puzzle->cur_node = &puzzle->node_stack[puzzle->node_stack_top];
	sync_cache_stacks(puzzle);
}
