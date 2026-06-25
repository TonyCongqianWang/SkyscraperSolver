/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_GAC_H
# define PRUNE_GAC_H

# include "puzzle_structs.h"
# include "strategy_config.h"

void	prune_gac(t_puzzle *puzzle, t_gac_config *config);

#endif
