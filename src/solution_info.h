/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   solution_info.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef SOLUTION_INFO_H
# define SOLUTION_INFO_H
# include "puzzle_structs.h"

int		init_sol_info(t_sol_info *info, int exhausted, t_sol_count registered);
int		update_sol_info(const t_sol_info *child, t_sol_info *aggregate);
void	finalize_valid_depth(t_sol_info *result, const t_node_state *node);
int		get_valid_depth(const t_node_state *node);
int		check_sol_target(t_sol_info *info, t_node_state *node);

#endif
