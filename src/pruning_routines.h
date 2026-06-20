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

# include "puzzle_structs.h"
# include "strategy_config.h"

typedef struct s_prune_routine_config
{
	int					run_check_constr;
	int					run_gac;
	t_gac_config		gac;
	int					run_lookahead;
	t_lookahead_config	lookahead;
}	t_prune_routine_cfg;

void	get_prune_cfg_light(t_prune_routine_cfg *cfg);
void	get_prune_cfg_medium(t_prune_routine_cfg *cfg);
void	get_prune_cfg_heavy(t_prune_routine_cfg *cfg);

void	run_pruning_routine(t_puzzle *puzzle, const t_prune_routine_cfg *cfg);

#endif
