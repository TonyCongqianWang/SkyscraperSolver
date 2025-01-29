/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_utlilty.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:36 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 00:07:44 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>
#include "print_utility.h"

void	print_solution_grid(t_puzzle *puzzle)
{
	int		counter;
	char	val;

	counter = 0;
	while (counter < puzzle->size * puzzle->size)
	{
		val = '0' + puzzle->grid_vals[counter];
		write(1, &val, 1);
		if (counter % puzzle->size != puzzle->size - 1)
		{
			write(1, " ", 1);
		}
		else
		{
			write(1, "\n", 1);
		}
		counter++;
	}
}

void	print_bmp_grid(t_puzzle *puzzle, int cell_val)
{
	int		counter;
	char	print_val;
	int		bitmap;

	counter = 0;
	while (counter < puzzle->size * puzzle->size)
	{
		bitmap = puzzle->node_state.valid_val_bmps[counter];
		bitmap >>= (cell_val - 1);
		bitmap &= 1;
		print_val += '0' + bitmap;
		write(1, &print_val, 1);
		if (counter % puzzle->size != puzzle->size - 1)
		{
			write(1, " ", 1);
		}
		else
		{
			write(1, "\n", 1);
		}
		counter++;
	}
}

void	print_score_grid(t_puzzle *puzzle)
{
	int		cell_idx;
	int		bit_idx;
	char	val;
	int		bitmap;

	cell_idx = 0;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		val = '0' + puzzle->size;
		bitmap = puzzle->node_state.valid_val_bmps[cell_idx];
		bit_idx = 0;
		while (bit_idx < puzzle->size)
		{
			val -= bitmap & 1;
			bitmap >>= 1;
			bit_idx++;
		}
		write(1, &val, 1);
		if (cell_idx % puzzle->size != puzzle->size - 1)
			write(1, " ", 1);
		else
			write(1, "\n", 1);
		cell_idx++;
	}
}

void	print_message(const char *str)
{
	while (*str)
	{
		write(1, str, 1);
		str++;
	}
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
