/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_grid.h                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 21:09:43 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRINT_GRID_H
# define PRINT_GRID_H
# include "puzzle_structs.h"

void	print_solution_grid(t_puzzle *grid, int append_nl);
void	print_bmp_grid(t_puzzle *puzzle, int cell_val);
void	print_bound_grid(t_node_state *node_state, int is_ub);

#endif
