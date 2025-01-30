/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   print_utlilty.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42heilbronn.de>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:36 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 11:15:16 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>
#include "print_utility.h"
#include "cell_bitmaps.h"

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

void	print_bmp_grid(t_puzzle *puzzle, int cell_val, int add_nl)
{
	int		cell_idx;
	char	print_val;
	t_node_state *node_state;

	cell_idx = 0;
	node_state = &puzzle->node_state;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		print_val = '0';
		print_val += is_valid_value(node_state, cell_idx, cell_val) != 0;
		write(1, &print_val, 1);
		if (cell_idx % puzzle->size != puzzle->size - 1)
		{
			write(1, " ", 1);
		}
		else
		{
			write(1, "\n", 1);
		}
		cell_idx++;
	}
	if (add_nl)
		write(1, "\n", 1);
}

void	print_score_grid(t_puzzle *puzzle)
{
	int		cell_idx;
	char	cell_val;
	char	print_val;
	t_node_state *node_state;

	cell_idx = 0;
	node_state = &puzzle->node_state;
	while (cell_idx < puzzle->size * puzzle->size)
	{
		print_val = '0' + puzzle->size;
		cell_val = 1;
		while (cell_val < puzzle->size)
		{
			print_val -= is_valid_value(node_state, cell_idx, cell_val) != 0;
			cell_val++;
		}
		write(1, &print_val, 1);
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
