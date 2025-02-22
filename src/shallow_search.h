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

void	tighten_grid_cell_bounds(t_puzzle *puzzle, int depth);
int		tighten_cell_bounds(t_puzzle *puzzle, int idx, int depth);
int		is_reiterate_allowed(t_node_state *state);
int		check_val_validity(t_puzzle *grid, int cell_idx, int val, int depth);

#endif
