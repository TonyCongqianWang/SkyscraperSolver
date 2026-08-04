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
#include "solution_info.h"
#include "node_selection_cache.h"
#include "node_selection_transition.h"

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
	return (0);
}

static void	update_cache_entropy(t_node_order *cache, t_node_transition next,
				int rem_entropy, int is_neg)
{
	int	i;

	if (!cache)
		return ;
	i = 0;
	while (i < cache->count)
	{
		if (cache->entries[i].cell_idx == next.cell_idx
			&& cache->entries[i].cell_val == next.cell_val)
		{
			if (is_neg)
				cache->meta[i].entropy_neg = rem_entropy;
			else
				cache->meta[i].entropy_pos = rem_entropy;
			break ;
		}
		i++;
	}
}

static int	do_l_ahead_dive_internal(t_puzzle *puzzle, t_node_transition next,
		int depth, t_check_mode mode)
{
	t_sol_info			local_sols;
	t_node_state		old_state;
	t_node_state		*cur_node;
	int					is_neg;

	is_neg = (depth < 0);
	if (depth < 0)
		depth = -depth;
	cur_node = puzzle->cur_node;
	old_state = *(cur_node);
	transition_node(puzzle, depth);
	local_sols = tree_recursion(puzzle, next, mode, is_neg);
	if (local_sols.solutions_found > 0)
		update_cache_entropy(old_state.order_cache, next,
			cur_node->remaining_entropy, is_neg);
	if (!is_neg)
	{
		old_state.lookahead_scores[next.cell_idx][(int)next.cell_val]
			= (double)(old_state.remaining_entropy
				- cur_node->remaining_entropy);
	}
	*(cur_node) = old_state;
	sync_cache_stacks(puzzle);
	return (local_sols.solutions_found > 0);
}

int	do_l_ahead_dive(t_puzzle *puzzle, t_node_transition next, int depth,
		t_check_mode mode)
{
	return (do_l_ahead_dive_internal(puzzle, next, depth, mode));
}

int	do_l_ahead_dive_neg(t_puzzle *puzzle, t_node_transition next, int depth,
		t_check_mode mode)
{
	return (do_l_ahead_dive_internal(puzzle, next, -depth, mode));
}
