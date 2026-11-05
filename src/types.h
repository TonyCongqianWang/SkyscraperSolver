/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   types.h                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/05 00:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/11/05 00:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef TYPES_H
# define TYPES_H

/* Bitmasks and counters. */
typedef unsigned short		t_u16;
typedef unsigned long long	t_u64;
typedef t_u64				t_sol_count;
typedef t_u64				t_node_count;

/* Signed DP bound: -1 denotes an unreachable state. */
typedef signed char			t_dp_bound;


#endif
