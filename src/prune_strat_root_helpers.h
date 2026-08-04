/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_root_helpers.h                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_STRAT_ROOT_HELPERS_H
# define PRUNE_STRAT_ROOT_HELPERS_H

# include "pruning_routines.h"

void	setup_cfg_thresholds(t_prune_routine_cfg *cfg, int remaining_entropy);
void	setup_cfg_bounds(t_prune_routine_cfg *cfg, int num_unset, int size);

#endif
