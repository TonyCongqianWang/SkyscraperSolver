/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_grid.h                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 18:47:49 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRINT_GRID_H
# define PRINT_GRID_H
# include "puzzle_structs.h"

void	print_score_grid(t_puzzle *puzzle);
void	print_solution_grid(t_puzzle *grid);
void	print_bmp_grid(t_puzzle *puzzle, int cell_val, int add_nl);

#endif
