/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_dirty_constraints.h                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/21 15:28:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/21 15:28:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUSH_DIRTY_CONSTRAINTS_H
# define PUSH_DIRTY_CONSTRAINTS_H
# include "puzzle_structs.h"

void	push_dirty_constraints(t_node_state *state, int cell_idx);

#endif
