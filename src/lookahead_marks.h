/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   lookahead_marks.h                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef LOOKAHEAD_MARKS_H
# define LOOKAHEAD_MARKS_H
# include "puzzle_structs.h"

void	init_lookahead_marks(t_lookahead_ctx *ctx, t_lookahead_ctx *parent);
void	mark_lookahead_leaf(t_node_state *node);
int		is_lookahead_assignment_marked(const t_lookahead_ctx *ctx,
			t_node_transition next);

#endif
