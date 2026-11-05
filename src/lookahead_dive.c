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

t_dive_result	do_l_ahead_dive(t_puzzle *puzzle, t_node_transition next,
		int depth, t_check_mode mode)
{
	return (do_l_ahead_dive_internal(puzzle, next, depth, mode));
}

t_dive_result	do_l_ahead_dive_neg(t_puzzle *puzzle, t_node_transition next,
		int depth, t_check_mode mode)
{
	if (puzzle->cur_node->is_in_neg_lookahead)
		return (DIVE_SKIP);
	return (do_l_ahead_dive_internal(puzzle, next, -depth, mode));
}
