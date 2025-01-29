/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_checking.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:47 by towang            #+#    #+#             */
/*   Updated: 2025/01/29 17:03:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CONSTRAINT_CHECKING_H
# define CONSTRAINT_CHECKING_H
# include "puzzle_structs.h"

int		check_active_constr(t_puzzle *puzzle);
void	reverse_constr_direction(t_puzzle *constr);
int		update_constr_state(t_puzzle *constr, int insert_idx);
void	set_active_constraint(t_puzzle *puzzle, int constr_idx);

#endif
