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
# include "puzzle_structs.h"

typedef enum e_search_result
{
	SEARCH_CONTINUE = 0,
	SEARCH_TERMINATE = 1,
	SEARCH_PROCEED_TO_BRANCH = -1
}	t_search_result;

typedef struct s_search_frame
{
	t_sol_info			node_sols;
	t_node_transition	next;
}		t_search_frame;

/* tree_search.c */
t_sol_info		tree_search(t_puzzle *puzzle);
t_sol_info		tree_recursion(t_puzzle *puzzle, t_node_transition next);
int				has_reached_terminal_state(t_node_state *cur_node);
t_sol_info		handle_leaf_node(t_puzzle *puzzle);

/* tree_search_step.c */
void			backtrack_to_parent(t_puzzle *puzzle, int *d,
					t_search_frame *frames);
void			descend_to_child(t_puzzle *puzzle, int *d,
					t_search_frame *frames);
t_search_result	check_backtrack(t_puzzle *puzzle, int *d, int start_d,
					t_search_frame *frames);
t_search_result	process_frame(t_puzzle *puzzle, int *d, int start_d,
					t_search_frame *frames);

#endif
