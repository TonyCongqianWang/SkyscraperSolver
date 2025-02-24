/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   shallow_search.h                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 20:46:14 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef SHALLOW_SEARCH_H
# define SHALLOW_SEARCH_H
# include "puzzle_structs.h"

void	reduce_grid_cell_options(t_puzzle *puzzle, int depth);

#endif
