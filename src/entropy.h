/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   entropy.h                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/15 11:35:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/15 11:35:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef ENTROPY_H
# define ENTROPY_H

# define ENTROPY_SCALE 1000

/* Scaled log2 lookup table: g_log2_table[k] ≈ log2(k) * 1000 */
static const int	g_log2_table[10] = {
	0,
	0,
	1000,
	1585,
	2000,
	2322,
	2585,
	2807,
	3000,
	3170
};

/* SPSA-tunable weights (scaled by 1000) */
static const int	g_weight_cell = 2000;
static const int	g_weight_constr = 1000;

struct s_node_state;
struct s_puzzle;

int		entropy_delta_cell(int old_count);
int		entropy_delta_constr(int old_count);
int		compute_initial_entropy(struct s_node_state *node, int size);
int		compute_max_entropy(int size);
int		isqrt_approx(long long n);

#endif
