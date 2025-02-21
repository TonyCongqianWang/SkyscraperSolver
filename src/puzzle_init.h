/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   puzzle_init.h                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 18:20:38 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUZZLE_INIT_H
# define PUZZLE_INIT_H
# include "puzzle_structs.h"

void	init_puzzle(t_puzzle *puzzle, int size);
void	init_grid_and_bmps(t_puzzle *puzzle, int size);
void	init_constraint(t_puzzle *puzzle, int idx, int size);
void	init_state_fields(t_puzzle *puzzle, int size);

#endif
