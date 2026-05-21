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

int	init_sol_info(t_sol_info *info, int min_nunset, int solutions_found);
int	update_sol_info(t_sol_info *n_info, t_sol_info *o_info);
int	check_sol_target(t_sol_info *info, t_node_state *node);
int	update_sol_target(t_sol_info *info, t_node_state *node);

#endif
