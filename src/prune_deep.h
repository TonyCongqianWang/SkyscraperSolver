/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_deep.h                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_DEEP_H
# define PRUNE_DEEP_H

# include "puzzle_structs.h"

void	prune_deep(t_puzzle *puzzle);
int		should_skip_prune_deep(t_puzzle *puzzle);

#endif
