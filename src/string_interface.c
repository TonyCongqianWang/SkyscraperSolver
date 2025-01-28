/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   string_interface.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:36 by towang            #+#    #+#             */
/*   Updated: 2025/01/28 20:55:43 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "string_interface.h"
#include "puzzle_init.h"

int	parse_puzzle_size_from_string(char *str)
{
	int		space_expected;
	int		counter;

	counter = 0;
	space_expected = 0;
	while (*str)
	{
		if (space_expected && *str != ' ')
			return (0);
		else if (!space_expected && (*str < '1' || *str > '9'))
			return (0);
		else if (!space_expected)
			counter++;
		space_expected = !space_expected;
		str++;
	}
	if (!space_expected)
		return (0);
	if (counter % 4 != 0)
		return (0);
	if ((counter / 4) > 9 || (counter / 4) < 1)
		return (0);
	return (counter / 4);
}

int	init_puzzle_from_str(t_puzzle *puzzle, char *str)
{
	int		size;
	int		word_idx;
	int		val;
	int		pair_idx;

	size = parse_puzzle_size_from_string(str);
	if (!size)
		return (0);
	init_puzzle(puzzle, size);
	word_idx = 0;
	while (word_idx < 4 * size)
	{
		val = str[2 * word_idx] - '0';
		if (val > size)
			return (0);
		pair_idx = word_idx - (word_idx / size / 2) * size;
		if ((word_idx / size) % 2 == 0)
			puzzle->constraint_pairs[pair_idx].fwd_val = val;
		else
			puzzle->constraint_pairs[pair_idx - size].bwd_val = val;
		word_idx++;
	}
	return (1);
}

void	add_constr_values(t_puzzle *puzzle, int vals[], int size)
{
	int		idx;
	int		pair_idx;

	idx = 0;
	while (idx < 4 * size)
	{
		pair_idx = idx - (idx / size / 2) * size;
		if ((idx / size) % 2 == 0)
			puzzle->constraint_pairs[pair_idx].fwd_val = vals[idx];
		else
			puzzle->constraint_pairs[pair_idx - size].bwd_val = vals[idx];
		idx++;
	}
}
