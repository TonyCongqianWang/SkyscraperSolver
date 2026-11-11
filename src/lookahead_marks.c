/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   lookahead_marks.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "lookahead_marks.h"

void	init_lookahead_marks(t_lookahead_ctx *ctx, t_lookahead_ctx *parent)
{
	int	i;

	ctx->parent = parent;
	ctx->probe_pass = LOOKAHEAD_NONE;
	ctx->positive_probe_depth = 0;
	ctx->probe_nesting_depth = 0;
	i = 0;
	while (i < MAX_CELL_COUNT)
		ctx->explored_assignments[i++] = 0;
}

/* Record only assignments on a completed, valid probe leaf. */
void	mark_lookahead_leaf(t_node_state *node)
{
	t_lookahead_ctx	*ctx;
	int				i;
	int				val;

	ctx = node->lookahead_ctx;
	if (!ctx || ctx->probe_pass != LOOKAHEAD_POS
		|| ctx->positive_probe_depth <= 1
		|| node->tree.lookahead_depth != ctx->probe_nesting_depth)
		return ;
	i = -1;
	while (++i < node->size * node->size)
	{
		val = node->domain.vals[i];
		if (val && !ctx->probe_base_vals[i])
			ctx->explored_assignments[i] |= (1U << (val - 1));
	}
}

int	is_lookahead_assignment_marked(const t_lookahead_ctx *ctx,
			t_node_transition next)
{
	return (ctx->probe_pass == LOOKAHEAD_POS
		&& ctx->positive_probe_depth > 1
		&& (ctx->explored_assignments[next.cell_idx]
			& (1U << (next.cell_val - 1))));
}
