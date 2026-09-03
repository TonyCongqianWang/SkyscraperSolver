/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_bucket.h                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/03 14:30:00 by towang            #+#    #+#             */
/*   Updated: 2026/09/03 14:30:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_STRAT_BUCKET_H
# define PRUNE_STRAT_BUCKET_H

# include "puzzle_structs.h"

int	get_depth_bucket(int depth, int squared_size, int size);
int	prune_strat_depth_bucket(t_puzzle *puzzle, int bucket);

#endif
