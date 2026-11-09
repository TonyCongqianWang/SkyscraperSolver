/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   check_node_validity.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/02 23:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/02 23:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CHECK_NODE_VALIDITY_H
# define CHECK_NODE_VALIDITY_H
# include "grid_interface.h"

t_check_mode	select_search_check_mode(const t_node_state *node,
					t_check_mode mode);
int				check_node_validity(t_solver_state *puzzle, t_check_mode mode);

#endif
