/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_io.h                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRINT_IO_H
# define PRINT_IO_H
# include "puzzle_structs.h"

void	put_char(const char ch);
void	print_message(const char *str);
void	print_value(const char *descr, unsigned long long value);
void	print_error(const char *str);
void	put_number(unsigned long long nbr);

#endif
