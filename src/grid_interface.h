/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   grid_interface.h                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/06 16:44:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/06 16:44:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef GRID_INTERFACE_H
# define GRID_INTERFACE_H

# include "puzzle_structs.h"

typedef struct s_grid_update
{
	int	cell_idx;
	int	val;
}				t_grid_update;

int		set_cell_val(t_puzzle *puzzle, int cell_idx, int val,
			t_check_mode mode);
int		set_cell_invalid(t_puzzle *puzzle, int cell_idx, int val,
			t_check_mode mode);
int		set_cell_vals_batch(t_puzzle *puzzle,
			const t_grid_update *updates, int count, t_check_mode mode);
int		set_cells_invalid_batch(t_puzzle *puzzle,
			const t_grid_update *updates, int count, t_check_mode mode);

#endif
