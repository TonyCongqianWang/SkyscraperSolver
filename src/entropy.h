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
# include "params_int.h"
# include "puzzle_structs.h"

# define ENTROPY_SCALE 1024
# define ENTROPY_SCALE_SHIFT 10

/* Scaled log2 lookup table: g_log2_table[k] ≈ log2(k) * 1024 */
static const int	g_log2_table[10] = {
	0,
	0,
	1024,
	1623,
	2048,
	2378,
	2647,
	2875,
	3072,
	3246
};

int		get_weight_cell(void);
int		get_weight_constr(void);
int		entropy_delta_cell(int old_count);
int		entropy_delta_constr(int old_count);
int		compute_initial_entropy(t_node_state *node, int size);
int		compute_max_entropy(int size);
int		compute_constr_entropy(t_node_state *node, int idx, int size);
double	get_relative_constr_entropy(t_node_state *node, int idx, int size);

#endif
