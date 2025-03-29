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

void	put_char(const char ch)
{
	if (!write(1, &ch, 1))
		return ;
}

void	print_message(const char *str)
{
	while (*str)
	{
		put_char(*str);
		str++;
	}
	put_char('\n');
}

void	print_value(const char *descr, unsigned long long value)
{
	while (*descr)
	{
		put_char(*descr);
		descr++;
	}
	put_char(':');
	put_char(' ');
	put_number(value);
	put_char('\n');
}

void	print_error(const char *str)
{
	(void)(write(2, "Error: ", 7) + 1);
	while (*str)
	{
		(void)(write(2, str, 1) + 1);
		str++;
	}
	(void)(write(2, "\n", 1) + 1);
}

void	put_number(unsigned long long nbr)
{
	char	val;

	val = '0';
	if (nbr >= 10)
		put_number(nbr / 10);
	val += nbr % 10;
	put_char(val);
}
