/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_utility.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:39 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 19:03:37 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRINT_UTILITY_H
# define PRINT_UTILITY_H
# include "puzzle_structs.h"

void	print_message(const char *str);
void	print_error(const char *str);
void	print_value(const char *descr, unsigned long long value);
void	put_number(unsigned long long nbr);

#endif
