/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_cfg_setup.h                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/04 17:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/08/04 17:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_STRAT_CFG_SETUP_H
# define PRUNE_STRAT_CFG_SETUP_H

# include "pruning_routines.h"

typedef struct s_prune_limits
{
	int		gac_min_entropy;
	int		constr_min_entropy;
	int		lh_continue_min_entropy;
	double	lh_continue_slope;
	int		gac_local_min_entropy;
	int		gac_local_max_entropy;
	int		gac_global_min_entropy;
	int		constr_local_min_entropy;
	int		constr_local_max_entropy;
	int		constr_global_min_entropy;
	int		lh_constr_local_min_entropy;
	int		lh_constr_local_max_entropy;
	int		lh_constr_global_min_entropy;
	int		lh_gac_local_min_entropy;
	int		lh_gac_local_max_entropy;
	int		lh_gac_global_min_entropy;
}	t_prune_limits;

void	setup_cfg_thresholds(t_prune_routine_cfg *cfg,
			const t_prune_limits *lim, int remaining_entropy);
void	setup_cfg_bounds(t_prune_routine_cfg *cfg,
			const t_prune_limits *lim, int num_unset, int size);

#endif
