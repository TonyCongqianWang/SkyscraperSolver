/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   puzzle_solver.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUZZLE_SOLVER_H
# define PUZZLE_SOLVER_H
# include "puzzle_structs.h"

int		solve_puzzle(t_puzzle *puzzle);
int		tree_search(t_puzzle *puzzle, int depths);
int		score_search_cell_candidate(t_puzzle *puzzle, int idx);
int		try_get_next_transition(t_puzzle* puzzle, t_node_transition* next);
int		get_next_tree_search_cell(t_puzzle *puzzle);

#endif
