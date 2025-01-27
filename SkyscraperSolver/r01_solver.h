/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   r01_solver.h                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2025/01/27 21:47:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef R01_SOLVER_H
# define R01_SOLVER_H
# include "r01_grid.h"

t_r01_grid	r01_solve_puzzle(t_r01_grid *puzzle);
t_r01_grid	r01_tree_search(t_r01_grid *puzzle, int depths, int score_depths);
int			r01_score_grid_idx(t_r01_grid *puzzle, int idx, int score_depths);
int			r01_get_next_grid_idx(t_r01_grid *puzzle, int score_depths);

#endif