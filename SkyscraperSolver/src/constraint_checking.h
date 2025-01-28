/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_checking.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:47 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 18:19:07 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CONSTRAINT_CHECKING_H
# define CONSTRAINT_CHECKING_H
# include "puzzle_structs.h"

int		check_active_constr(t_puzzle *puzzle);
void	reverse_constr_direction(t_constraint_state *constr);
void	insert_val(t_constraint_state *constr, int val);
void	update_constr_bounds(t_constraint_state *constr);

#endif
