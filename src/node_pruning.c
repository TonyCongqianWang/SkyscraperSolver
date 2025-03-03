/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_pruning.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:02:06 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_pruning.h"
#include "grid_manipulation.h"
#include "cell_bounds.h"
#include "puzzle_solver.h"
#include "node_selection.h"
#include "constraint_checking.h"

static int	init_pruning_state(t_puzzle *puzzle);
static int	keep_pruning(t_puzzle *puzzle);
static int	check_validity(t_puzzle *puzzle, t_node_transition next);
static int	check_only_constr(t_puzzle *puzzle, t_node_transition next);

void	prune_node(t_puzzle *puzzle)
{
	t_node_transition	tr;

	if (!init_pruning_state(puzzle))
		return ;
	while (keep_pruning(puzzle))
	{
		tr.cell_idx = 0;
		tr.cell_val = 1;
		while (try_get_next_transition(puzzle, &tr))
		{
			if (!check_validity(puzzle, tr))
			{
				set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val);
				puzzle->pruning.last_iteration_succeeded = 1;
			}
			tr.cell_val++;
		}
	}
}

static int	init_pruning_state(t_puzzle *puzzle)
{
	const double	min_unset_quotient_reit = 0.67;
	double			unset_quotient;
	t_node_state	*node;

	node = puzzle->cur_node;
	unset_quotient = node->num_unset;
	unset_quotient /= puzzle->size * puzzle->size;
	puzzle->pruning.max_pruning_depth = 1;
	puzzle->pruning.cur_pruning_depth = 0;
	puzzle->pruning.can_reiterate = unset_quotient > min_unset_quotient_reit;
	if (node->sub_node_depth == 0
		&& node->cur_depth == 0)
	{
		puzzle->pruning.max_pruning_depth = puzzle->size / 2;
		puzzle->pruning.cur_pruning_depth = -1;
	}
	puzzle->pruning.last_iteration_succeeded = 0;
	return (1);
}

static int	keep_pruning(t_puzzle *puzzle)
{
	t_node_pruning_state	*pruning;

	pruning = &puzzle->pruning;
	if (pruning->cur_pruning_depth <= 0)
	{
		pruning->cur_pruning_depth++;
		return (1);
	}
	if (pruning->last_iteration_succeeded && pruning->can_reiterate
		&& pruning->cur_pruning_depth == 1)
	{
		pruning->last_iteration_succeeded = 0;
		return (1);
	}
	else if (pruning->cur_pruning_depth < pruning->max_pruning_depth)
	{
		pruning->last_iteration_succeeded = 0;
		pruning->cur_pruning_depth *= 2;
		return (1);
	}
	return (0);
}

static int	check_validity(t_puzzle *puzzle, t_node_transition next)
{
	t_node_state	old_state;
	int				is_valid;
	int				cur_depth;
	int				pruning_depth;

	cur_depth = puzzle->cur_node->cur_depth;
	pruning_depth = puzzle->pruning.cur_pruning_depth;
	if (pruning_depth <= 0)
		return (check_only_constr(puzzle, next));
	old_state = *(puzzle->cur_node);
	puzzle->cur_node->max_depth = cur_depth + pruning_depth;
	puzzle->cur_node->cur_depth++;
	puzzle->cur_node->sub_node_depth++;
	set_grid_val(puzzle->cur_node, next.cell_idx, next.cell_val, 1);
	is_valid = tree_search(puzzle);
	if (!is_valid || !puzzle->cur_node->is_complete)
		*(puzzle->cur_node) = old_state;
	return (is_valid);
}

static int	check_only_constr(t_puzzle *puzzle, t_node_transition next)
{
	int				is_valid;

	puzzle->cur_node->grid.vals[next.cell_idx] = next.cell_val;
	is_valid = check_constraints(puzzle, next.cell_idx);
	puzzle->cur_node->grid.vals[next.cell_idx] = 0;
	return (is_valid);
}
