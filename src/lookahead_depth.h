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

/* Rows: speculative nesting level; columns: light, medium, heavy. */
/* A zero entry disables lookahead for that tier at that nesting level. */
extern const int	g_lookahead_probe_depth[][PRUNE_TIER_COUNT];

#endif
