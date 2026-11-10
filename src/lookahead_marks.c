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
	i = 0;
	while (i < MAX_CELL_COUNT)
		ctx->explored_assignments[i++] = 0;
}

/* These conditional visits restrict probe eligibility, never the domain. */
void	mark_lookahead_assignment(t_lookahead_ctx *ctx, t_node_transition next)
{
	while (ctx)
	{
		if (ctx->probe_pass == LOOKAHEAD_POS)
			ctx->explored_assignments[next.cell_idx]
				|= (1U << (next.cell_val - 1));
		ctx = ctx->parent;
	}
}

int	is_lookahead_assignment_marked(const t_lookahead_ctx *ctx,
			t_node_transition next)
{
	return (ctx->probe_pass == LOOKAHEAD_POS
		&& (ctx->explored_assignments[next.cell_idx]
			& (1U << (next.cell_val - 1))));
}
