/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   r01_io.h                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/27 21:47:14 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef R01_IO_H
# define R01_IO_H
# include "r01_grid.h"

int		r01_parse_input_size(char *str);
void	r01_parse_input(t_r01_grid *grid, t_r01_constraints *cons, char *str);
void	r01_print_grid(t_r01_grid *grid);
void	r01_print_error(void);

#endif