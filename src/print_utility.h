/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_utility.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/29 23:58:44 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRINT_UTILITY_H
# define PRINT_UTILITY_H
# include "puzzle_structs.h"

void	print_score_grid(t_puzzle *puzzle);
void	print_solution_grid(t_puzzle *grid);
void	print_message(const char *str);
void	print_error(const char *str);
void	print_bmp_grid(t_puzzle *puzzle);

#endif
