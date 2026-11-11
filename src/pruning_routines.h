/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pruning_routines.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/20 23:59:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/20 23:59:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNING_ROUTINES_H
# define PRUNING_ROUTINES_H

# include "grid_interface.h"
# include "strategy_config.h"

typedef struct s_prune_routine_config
{
	t_selectivity_level	selectivity;
	double				check_constr_min_entropy;
	double				check_constr_max_entropy;
	int					check_constr_global_min_entropy;
	t_lookahead_config	lookahead;
}	t_prune_routine_cfg;

/* A processed tier returns 1, even without domain changes or after a skip. */
int		run_pruning_routine(t_solver_state *puzzle,
			const t_prune_routine_cfg *cfg, int cfg_idx);

#endif
