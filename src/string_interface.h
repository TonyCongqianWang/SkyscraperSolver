/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   string_interface.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 20:22:14 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef STRING_INTERFACE_H
# define STRING_INTERFACE_H
# include "puzzle_structs.h"

int		init_puzzle_from_constr_str(t_puzzle *puzzle, char *str);
int		set_puzzle_grid_to_str_vals(t_puzzle *puzzle, char *str);

#endif
