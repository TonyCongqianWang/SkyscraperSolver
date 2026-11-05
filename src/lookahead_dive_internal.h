/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   lookahead_dive_internal.h                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/05 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/05 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef LOOKAHEAD_DIVE_INTERNAL_H
# define LOOKAHEAD_DIVE_INTERNAL_H
# include "lookahead_dive.h"

t_dive_result	do_l_ahead_dive_internal(t_puzzle *puzzle,
					t_node_transition next, int depth, t_check_mode mode);

#endif
