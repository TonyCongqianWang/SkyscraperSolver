/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_checking.h                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:47 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 20:46:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CONSTRAINT_CHECKING_H
# define CONSTRAINT_CHECKING_H
# include "puzzle_structs.h"

int		check_constraints(t_puzzle *puzzle, int insert_idx);
int		check_active_constr(t_puzzle *puzzle);
int		check_constr_bounds_violations(t_constraint_bounds *constr);

#endif
