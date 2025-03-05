/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   solution_storage.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef SOLUTION_STORAGE_H
# define SOLUTION_STORAGE_H
# include "puzzle_structs.h"

void	init_solution_storage(t_puzzle *puzzle, unsigned long long max_sols);
void	free_solution_storage(t_puzzle *puzzle);
void	store_node_if_solution(t_puzzle *puzzle);

#endif
