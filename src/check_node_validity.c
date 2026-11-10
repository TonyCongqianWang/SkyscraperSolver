/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   check_node_validity.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/02 23:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/02 23:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "check_node_validity.h"
#include "push_dirty_constraints.h"
#include "constraint_selection.h"
#include "constraint_checking.h"
#include "prune_check_constr.h"
#include "math_utils.h"

static void	process_dirty_entry(t_solver_state *puzzle, int entry,
		t_check_mode mode)
{
	t_node_state	*node;
	int				idx;

	node = puzzle->cur_node;
	idx = entry / 2;
	set_active_constraint(puzzle, idx);
	if (entry % 2)
		reverse_constr_direction(puzzle);
	if (mode.run_constr && !check_active_constr(puzzle))
		node->domain.is_invalid = 1;
	if (node->domain.is_invalid)
		return ;
	if (mode.run_prop)
		process_constraint(puzzle, idx, node->size, &mode.constr);
}

static t_check_mode	get_pass_mode(t_solver_state *puzzle, t_check_mode mode,
		int iter)
{
	int	req_entropy;

	if (iter == 0)
		return (mode);
	req_entropy = (int)((double)mode.lookahead_continue_min_entropy
			* (1.0 + mode.lookahead_continue_slope * (double)iter));
	if (puzzle->cur_node->domain.remaining_entropy >= req_entropy)
		return (mode);
	return (g_check_constr);
}

static void	drain_dirty_constraints_mode(t_solver_state *puzzle,
		t_check_mode mode)
{
	t_dirty_constr_stack	local;
	int						entry;
	int						iter;
	t_check_mode			cur_mode;

	iter = 0;
	while (puzzle->cur_node->dirty_constrs.count > 0
		&& !puzzle->cur_node->domain.is_invalid)
	{
		local = puzzle->cur_node->dirty_constrs;
		puzzle->cur_node->dirty_constrs.count = 0;
		puzzle->cur_node->dirty_constrs.in_stack_bmp = 0;
		cur_mode = get_pass_mode(puzzle, mode, iter++);
		while (local.count > 0 && !puzzle->cur_node->domain.is_invalid)
		{
			entry = local.entries[(int)(--local.count)];
			local.in_stack_bmp &= ~(1ULL << entry);
			process_dirty_entry(puzzle, entry, cur_mode);
		}
	}
}

int	check_node_validity(t_solver_state *puzzle, t_check_mode mode)
{
	mode = select_search_check_mode(puzzle->cur_node, mode);
	drain_dirty_constraints_mode(puzzle, mode);
	return (!puzzle->cur_node->domain.is_invalid);
}
