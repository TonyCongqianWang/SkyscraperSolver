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

void	get_prune_cfg_light(t_prune_routine_cfg *cfg);
void	get_prune_cfg_medium(t_prune_routine_cfg *cfg);
void	get_prune_cfg_heavy(t_prune_routine_cfg *cfg);
int		calc_effective_global_min_entropy(int base_entropy, int num_unset);

#endif
