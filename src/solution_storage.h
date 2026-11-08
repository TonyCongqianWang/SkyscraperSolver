/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   solution_storage.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:51:38 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef SOLUTION_STORAGE_H
# define SOLUTION_STORAGE_H
# include "puzzle_structs.h"

typedef enum e_registration_kind
{
	REGISTRATION_NONE,
	REGISTRATION_PERMANENT,
	REGISTRATION_PROVISIONAL
}	t_registration_kind;

t_registration_kind	get_solution_registration(const t_solver_state *puzzle);
int					solution_limit_reached(const t_solver_state *puzzle);
void				rollback_provisional_solution(t_solver_state *puzzle);

int					init_solution_storage(t_solver_state *puzzle,
						t_sol_count max_sols);
void				free_solution_storage(t_solver_state *puzzle);
int					store_node_if_solution(t_solver_state *puzzle);

#endif
