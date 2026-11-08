/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   tree_search.h                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef TREE_SEARCH_H
# define TREE_SEARCH_H
# include "grid_interface.h"

typedef enum e_leaf_state
{
	LEAF_NONE,
	LEAF_INVALID,
	LEAF_COMPLETE,
	LEAF_DEPTH_LIMIT,
	LEAF_PROGRESS_LIMIT
}	t_leaf_state;

typedef enum e_search_result
{
	SEARCH_CONTINUE = 0,
	SEARCH_TERMINATE = 1,
	SEARCH_PROCEED_TO_BRANCH = -1
}	t_search_result;

typedef struct s_search_frame
{
	t_sol_info					node_sols;
	t_node_transition			next;
	const t_lookahead_config	*probe_config;
	t_lookahead_pass			probe_pass;
}		t_search_frame;

/* tree_search.c */
t_sol_info		tree_search(t_solver_state *puzzle);
t_sol_info		run_tree_search(t_solver_state *puzzle,
					const t_lookahead_config *config, t_lookahead_pass pass);
/* tree_search_transition.c */
void			execute_search_transition(t_solver_state *puzzle, int *d,
					t_search_frame *frames);
/* search_leaf.c */
t_leaf_state	classify_search_leaf(const t_node_state *node);
int				has_reached_terminal_state(t_node_state *cur_node);
t_sol_info		handle_leaf_node(t_solver_state *puzzle);

/* tree_search_frame.c */
void			backtrack_to_parent(t_solver_state *puzzle, int *d,
					t_search_frame *frames);
void			descend_to_child(t_solver_state *puzzle, int *d,
					t_search_frame *frames);
t_search_result	check_backtrack(t_solver_state *puzzle, int *d, int start_d,
					t_search_frame *frames);
t_search_result	process_search_frame(t_solver_state *puzzle, int *d,
					int start_d, t_search_frame *frames);

#endif
