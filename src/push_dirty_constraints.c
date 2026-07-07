/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_dirty_constraints.c                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/07 02:22:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/07 02:22:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "check_node_validity.h"

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
