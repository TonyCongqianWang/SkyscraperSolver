/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_utlilty.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:36 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:28:31 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>
#include "print_utility.h"
#include "cell_bitmaps.h"

void	print_message(const char *str)
{
	while (*str)
	{
		write(1, str, 1);
		str++;
	}
	write(1, "\n", 1);
}

void	print_value(const char *descr, unsigned long long value)
{
	while (*descr)
	{
		write(1, descr, 1);
		descr++;
	}
	write(1, ": ", 2);
	put_number(value);
	write(1, "\n", 1);
}

void	print_error(const char *str)
{
	write(2, "Error: ", 7);
	while (*str)
	{
		write(2, str, 1);
		str++;
	}
	write(2, "\n", 1);
}

void	put_number(unsigned long long nbr)
{
	char	val;

	val = '0';
	if (nbr >= 10)
		put_number(nbr / 10);
	val += nbr % 10;
	write(1, &val, 1);
}
