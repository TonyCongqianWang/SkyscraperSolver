/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   line_order.h                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:40:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:40:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef LINE_ORDER_H
# define LINE_ORDER_H

# include "puzzle_structs.h"

t_line_order	*get_line_order(t_node_state *node);
void			init_line_order_stack(t_puzzle *puzzle);
void			copy_line_order(t_puzzle *puzzle, int parent_idx);
void			sort_line_order(t_node_state *node);

#endif
