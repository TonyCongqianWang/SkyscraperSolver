/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac_domain.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_GAC_DOMAIN_H
# define PRUNE_GAC_DOMAIN_H

# include "puzzle_structs.h"

int		count_bits(int bmp);
void	eliminate_bmp_vals(t_node_state *state, int cell_idx, int u_bmp);
void	keep_only_values(t_node_state *state, int cell_idx, int keep_mask);
void	get_value_cells(t_node_state *state, int *cells, int count,
			int *value_cells);

#endif
