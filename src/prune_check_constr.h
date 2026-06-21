/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr.h                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */
#ifndef PRUNE_CHECK_CONSTR_H
# define PRUNE_CHECK_CONSTR_H

# include "puzzle_structs.h"
# include "strategy_config.h"

void	prune_check_constr(t_puzzle *puzzle, t_selectivity_level selectivity);

#endif
