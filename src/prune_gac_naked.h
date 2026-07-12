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
# include "prune_gac_domain.h"

void	analyse_naked_pairs(int *cells, int count, t_gac_batch *batch);
void	analyse_naked_triples(int *cells, int count, t_gac_batch *batch);
void	run_gac_naked(int *cells, int count,
			t_gac_config *config, t_gac_batch *batch);

#endif
