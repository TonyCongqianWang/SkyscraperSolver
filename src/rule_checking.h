/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rule_checking.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 20:22:14 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef RULE_CHECKING_H
# define RULE_CHECKING_H
# include "puzzle_structs.h"

typedef struct s_constr_check_state
{
	t_constraint_pair	constr_pair;
	int					seen_bmp;
	int					cur_max_height;
	int					cur_num_visible;
}		t_constr_check_state;

int		check_rule_violations(t_puzzle *puzzle);

#endif
