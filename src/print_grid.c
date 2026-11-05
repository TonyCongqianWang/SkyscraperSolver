/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_grid.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:36 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 23:14:29 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "print_grid.h"
#include "print_io.h"

void	print_solution_grid(t_puzzle *puzzle, int append_nl)
{
	int		counter;
	char	val;

	counter = 0;
	while (counter < puzzle->squared_size)
	{
		val = '0' + puzzle->cur_node->grid.vals[counter];
		put_char(val);
		if (counter % puzzle->size != puzzle->size - 1)
		{
			put_char(' ');
		}
		else
		{
			put_char('\n');
		}
		counter++;
	}
	if (append_nl)
		put_char('\n');
}
