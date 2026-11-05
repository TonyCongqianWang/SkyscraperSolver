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
# include <stdint.h>

/* Bitmasks and counters. */
typedef uint16_t			t_u16;
typedef uint64_t			t_u64;
typedef uint64_t			t_sol_count;
typedef uint64_t			t_node_count;

# define MAX_SOL_COUNT ((t_sol_count)-1)

/* Signed DP bound: -1 denotes an unreachable state. */
typedef int8_t				t_dp_bound;

#endif
