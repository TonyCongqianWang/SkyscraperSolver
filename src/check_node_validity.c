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
#include "constraint_selection.h"
#include "constraint_checking.h"

static void	push_entry(t_dirty_constr_stack *stack, int entry)
{
	t_u64	mask;

	mask = 1ULL << entry;
	if (stack->in_stack_bmp & mask)
		return ;
	stack->in_stack_bmp |= mask;
	stack->entries[(int)stack->count] = entry;
	stack->count++;
}

void	push_dirty_constraints(t_node_state *state, int cell_idx)
{
	int						constr_idx;
	t_dirty_constr_stack	*stack;
	t_constraint_pair		*pair;
	int						rel;

	stack = &state->dirty_constrs;
	rel = 0;
	while (rel < 2)
	{
		constr_idx = state->puzzle->grid_constr_map[cell_idx][rel];
		pair = &state->puzzle->constraint_pairs[constr_idx];
		if (pair->fwd_val != 0)
			push_entry(stack, constr_idx * 2);
		if (pair->bwd_val != 0)
			push_entry(stack, constr_idx * 2 + 1);
		rel++;
	}
}

void	drain_dirty_constraints(t_puzzle *puzzle)
{
	t_node_state			*node;
	t_dirty_constr_stack	*stack;
	int						entry;

	node = puzzle->cur_node;
	stack = &node->dirty_constrs;
	while (stack->count > 0 && !node->is_invalid)
	{
		entry = stack->entries[(int)(--stack->count)];
		stack->in_stack_bmp &= ~(1ULL << entry);
		set_active_constraint(puzzle, entry / 2);
		if (entry % 2)
			reverse_constr_direction(puzzle);
		if (!check_active_constr(puzzle))
			node->is_invalid = 1;
	}
}
