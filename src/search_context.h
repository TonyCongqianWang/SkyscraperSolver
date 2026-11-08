/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_context.h                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef SEARCH_CONTEXT_H
# define SEARCH_CONTEXT_H
# include "puzzle_structs.h"

typedef struct s_probe_request
{
	t_node_transition	next;
	t_check_mode		check_mode;
	int					depth;
}	t_probe_request;

typedef struct s_search_scope
{
	t_search_policy	policy;
	t_lookahead_ctx	*cursor;
}	t_search_scope;

void	enter_lookahead(t_node_state *node, t_lookahead_ctx *ctx,
			t_selectivity_level selectivity, t_search_scope *saved);
void	leave_lookahead(t_node_state *node, const t_search_scope *saved);
int		enter_probe(t_solver_state *puzzle, const t_probe_request *request,
			t_node_state *saved);
void	init_root_search_policy(t_node_state *node);
void	leave_probe(t_solver_state *puzzle, const t_node_state *saved);
void	apply_search_transition(t_solver_state *puzzle, t_node_transition next,
			t_check_mode mode, int is_neg);
void	enter_search_child(t_solver_state *puzzle, t_node_transition next,
			t_sol_count solutions_found);
void	leave_search_child(t_solver_state *puzzle);
void	set_search_bounds(t_node_state *node, int max_depth, int target);

#endif
