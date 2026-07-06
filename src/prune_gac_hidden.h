/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac_hidden.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_GAC_HIDDEN_H
# define PRUNE_GAC_HIDDEN_H

# include "puzzle_structs.h"
# include "grid_interface.h"

typedef struct s_hidden_param
{
	int		*cells;
	int		count;
	int		*val_cells;
}	t_hidden_param;

void	analyse_hidden_pairs(t_node_state *state, int *cells, int count,
			int *val_cells, t_grid_update *updates, int *update_count, int *pruned_masks);
void	analyse_hidden_triples(t_node_state *state, int *cells, int count,
			int *val_cells, t_grid_update *updates, int *update_count, int *pruned_masks);

#endif
