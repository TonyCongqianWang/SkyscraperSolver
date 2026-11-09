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
# include "math_log.h"

# define ENTROPY_SCALE 1024
# define ENTROPY_SCALE_SHIFT 10

int		get_weight_cell(int size);
int		get_weight_constr(int size);
int		entropy_delta_cell(int old_count, int size);
int		entropy_delta_constr(int old_count, int size);
int		compute_initial_entropy(t_node_state *node, int size);
int		compute_max_entropy(int size);
int		compute_constr_entropy(t_node_state *node, int idx, int size);
double	get_relative_constr_entropy(t_node_state *node, int idx, int size);

#endif
