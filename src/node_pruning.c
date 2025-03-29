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

static int	init_pruning_state(t_puzzle *puzzle, t_node_pruning_state *pruning);
static int	keep_pruning(t_puzzle *puzzle, t_node_pruning_state *pruning);
static int	check_validity(t_puzzle *puzzle, t_node_transition next, int depth);
static int	check_only_constr(t_puzzle *puzzle, t_node_transition next);

void	prune_node(t_puzzle *puzzle)
{
	t_node_pruning_state	pruning;
	t_node_transition		tr;
	int						counter;
	int						update_idx;

	puzzle->cur_node->cur_prune_nunset = puzzle->cur_node->num_unset + 1;
	init_pruning_state(puzzle, &pruning);
	while (keep_pruning(puzzle, &pruning))
	{
		tr.cell_idx = 0;
		tr.cell_val = 1;
		while (try_get_next_transition(puzzle, &tr))
		{
			tr.cell_val++;
			if (!pruning.tr_needs_check[tr.cell_idx][tr.cell_val - 2])
				continue ;
			pruning.tr_needs_check[tr.cell_idx][tr.cell_val - 2] = 0;
			if (!check_validity(puzzle, tr, pruning.cur_pruning_depth))
			{
				counter = 1;
				while (counter < puzzle->size)
				{
					update_idx = (tr.cell_idx / puzzle->size) * puzzle->size;
					update_idx += ((tr.cell_idx + counter) % puzzle->size);
					for (int val = 1; val <= puzzle->size; val++)
						pruning.tr_needs_check[update_idx][val - 1] = 1;
					counter++;
				}
				counter = 1;
				while (counter < puzzle->size)
				{
					update_idx = (tr.cell_idx + counter * puzzle->size);
					update_idx %= puzzle->size * puzzle->size;
					for (int val = 1; val <= puzzle->size; val++)
						pruning.tr_needs_check[update_idx][val - 1] = 1;
					counter++;
				}
				set_value_invalid(puzzle->cur_node, tr.cell_idx, tr.cell_val - 1);
				pruning.last_iteration_succeeded = 1;
			}
		}
	}
	puzzle->cur_node->last_prune_nunset = puzzle->cur_node->cur_prune_nunset;
}

static int	init_pruning_state(t_puzzle *puzzle, t_node_pruning_state *pruning)
{
	const double	min_unset_quotient_prune = 0.4;
	const double	min_unset_quotient_reit = 0.7;
	double			unset_quotient;
	t_node_state	*node;

	node = puzzle->cur_node;
	unset_quotient = node->num_unset;
	unset_quotient /= puzzle->size * puzzle->size;
	if (unset_quotient < min_unset_quotient_prune)
		return (0);
	if (node->cur_prune_nunset <= node->num_unset)
		return (1);
	else
		node->cur_prune_nunset = node->num_unset;
	for (int idx = 0; idx < puzzle->size * puzzle->size; idx++)
	{
		for (int val = 1; val <= puzzle->size; val++)
		{
			pruning->tr_needs_check[idx][val - 1] = 1;
		}
	}
	pruning->max_pruning_depth = 1;
	pruning->cur_pruning_depth = 0;
	pruning->can_reiterate = unset_quotient > min_unset_quotient_reit;
	if (node->sub_node_depth == 0
		&& node->cur_depth == 0)
	{
		pruning->cur_pruning_depth = -1;
	}
	pruning->last_iteration_succeeded = 0;
	return (1);
}

static int	keep_pruning(t_puzzle *puzzle, t_node_pruning_state *pruning)
{
	if (!init_pruning_state(puzzle, pruning))
		return (0);
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

static int	check_validity(t_puzzle *puzzle, t_node_transition next, int depth)
{
	t_node_state	old_state;
	int				is_valid;
	int				solution_found;

	if (depth <= 0)
		return (check_only_constr(puzzle, next));
	old_state = *(puzzle->cur_node);
	puzzle->cur_node->max_depth = puzzle->cur_node->cur_depth;
	puzzle->cur_node->max_depth += depth;
	puzzle->cur_node->cur_depth++;
	puzzle->cur_node->sub_node_depth++;
	set_grid_val(puzzle->cur_node, next.cell_idx, next.cell_val, 1);
	is_valid = tree_search(puzzle);
	solution_found = (is_valid && puzzle->cur_node->is_complete);
	if (solution_found && puzzle->max_solutions == 1)
		puzzle->cur_node->sub_node_depth--;
	else
		*(puzzle->cur_node) = old_state;
	return (is_valid && !(solution_found && puzzle->max_solutions != 1));
}

static int	check_only_constr(t_puzzle *puzzle, t_node_transition next)
{
	int				is_valid;

	puzzle->cur_node->grid.vals[next.cell_idx] = next.cell_val;
	is_valid = check_constraints(puzzle, next.cell_idx);
	puzzle->cur_node->grid.vals[next.cell_idx] = 0;
	return (is_valid);
}
