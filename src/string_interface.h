/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   string_interface.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 17:40:11 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef STRING_INTERFACE_H
# define STRING_INTERFACE_H
# include "puzzle_structs.h"

int		init_puzzle_from_str(t_puzzle *puzzle, char *str);
int		parse_puzzle_size_from_string(char *str);

#endif
