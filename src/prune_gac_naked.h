/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac_naked.h                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_GAC_NAKED_H
# define PRUNE_GAC_NAKED_H

# include "puzzle_structs.h"
# include "grid_interface.h"

void	analyse_naked_pairs(t_node_state *state, int *cells, int count, t_grid_update *updates, int *update_count, int *pruned_masks);
void	analyse_naked_triples(t_node_state *state, int *cells, int count, t_grid_update *updates, int *update_count, int *pruned_masks);

#endif
