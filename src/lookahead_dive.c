/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   lookahead_dive.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/05 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/05 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "lookahead_dive_internal.h"

t_probe_result	probe_assumption(t_solver_state *puzzle, t_node_transition next,
		int depth, t_check_mode mode)
{
	t_probe_result	result;

	result.outcome.exhausted = 0;
	result.outcome.solutions_registered = 0;
	result.status = DIVE_SKIP;
	result.remaining_entropy = -1;
	if (puzzle->cur_node->tree.lookahead_depth >= MAX_LOOKAHEAD_DEPTH)
		return (result);
	return (search_probe(puzzle, next, depth, mode));
}

t_probe_result	probe_exclusion(t_solver_state *puzzle, t_node_transition next,
		int depth, t_check_mode mode)
{
	t_probe_result	result;

	result.outcome.exhausted = 0;
	result.outcome.solutions_registered = 0;
	result.status = DIVE_SKIP;
	result.remaining_entropy = -1;
	if (puzzle->cur_node->tree.lookahead_depth >= MAX_LOOKAHEAD_DEPTH
		|| puzzle->cur_node->tree.neg_lookahead_depth
		>= MAX_NEG_LOOKAHEAD_DEPTH)
		return (result);
	return (search_probe(puzzle, next, -depth, mode));
}
