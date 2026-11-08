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

/* Indexed by pruning tier: light, medium, heavy. */
extern const int	g_lookahead_probe_depth[3];

#endif
