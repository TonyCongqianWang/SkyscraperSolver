/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pruning_configs.h                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/21 15:28:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/21 15:28:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNING_CONFIGS_H
# define PRUNING_CONFIGS_H
# include "pruning_routines.h"
# include "lookahead_depth.h"

void					init_prune_cfg(t_prune_routine_cfg *cfg, int tier);
t_selectivity_level		get_prune_tier_selectivity(int tier);
int						calc_effective_global_min_entropy(int base_entropy,
							int num_unset, int size);

#endif
