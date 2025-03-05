/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   argument_parsing.h                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 20:22:14 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef ARGUMENT_PARSING_H
# define ARGUMENT_PARSING_H
# include "puzzle_structs.h"

int	init_puzzle_from_argv(t_puzzle *puzzle, int argc, char **argv);

#endif
