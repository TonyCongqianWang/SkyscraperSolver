/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   lookahead_depth.h                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/26 11:52:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 11:52:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef LOOKAHEAD_DEPTH_H
# define LOOKAHEAD_DEPTH_H

# include "puzzle_structs.h"

/* Each nesting row has light, medium, heavy {positive, negative} pairs. */
/* Zero disables only the corresponding probe direction. */
extern const t_probe_depth	g_probe_depths[][PRUNE_TIER_COUNT];

#endif
