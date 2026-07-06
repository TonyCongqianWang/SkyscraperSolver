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
#include "prune_check_constr.h"
#include "prune_gac.h"

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

static void	process_dirty_entry(t_puzzle *puzzle, int entry, t_check_mode mode)
{
	t_node_state	*node;
	int				idx;
	t_gac_config	gac_cfg;

	node = puzzle->cur_node;
	idx = entry / 2;
	set_active_constraint(puzzle, idx);
	if (entry % 2)
		reverse_constr_direction(puzzle);
	if ((mode & CHECK_CONSTR) && !check_active_constr(puzzle))
		node->is_invalid = 1;
	if (node->is_invalid)
		return ;
	if (mode & CHECK_PROP)
		process_constraint(puzzle, idx, node->size);
	if (!node->is_invalid && (mode & CHECK_GAC))
	{
		gac_cfg.selectivity = SELECTIVITY_NONE;
		gac_cfg.max_k = 3;
		gac_cfg.analyse_naked = 1;
		gac_cfg.analyse_hidden = 1;
		analyse_gac_line(puzzle, idx % node->size, idx < node->size,
			&gac_cfg);
	}
}

void	drain_dirty_constraints_mode(t_puzzle *puzzle, t_check_mode mode)
{
	t_node_state			*node;
	t_dirty_constr_stack	local_stack;
	int						entry;

	node = puzzle->cur_node;
	while (node->dirty_constrs.count > 0 && !node->is_invalid)
	{
		local_stack = node->dirty_constrs;
		node->dirty_constrs.count = 0;
		node->dirty_constrs.in_stack_bmp = 0;
		while (local_stack.count > 0 && !node->is_invalid)
		{
			entry = local_stack.entries[(int)(--local_stack.count)];
			local_stack.in_stack_bmp &= ~(1ULL << entry);
			process_dirty_entry(puzzle, entry, mode);
		}
	}
}

int	check_node_validity(t_puzzle *puzzle, t_check_mode mode)
{
	drain_dirty_constraints_mode(puzzle, mode);
	return (!puzzle->cur_node->is_invalid);
}
