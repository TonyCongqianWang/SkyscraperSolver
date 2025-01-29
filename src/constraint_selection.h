/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   constraint_selection.h                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 21:31:47 by towang            #+#    #+#             */
/*   Updated: 2025/01/29 19:14:52 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CONSTRAINT_SELECTION_H
# define CONSTRAINT_SELECTION_H
# include "puzzle_structs.h"

void	set_active_constraint(t_puzzle *puzzle, int constr_idx);
void	reverse_constr_direction(t_puzzle *constr);
void	reset_constraint_bounds(t_puzzle *puzzle);

#endif
