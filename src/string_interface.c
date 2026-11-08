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
#include "grid_manipulation.h"

static int		parse_puzzle_size_from_constr_str(char *str);
static int		try_add_constr_values(t_solver_state *puzzle, char *str);

static int	parse_max_solution(char *str, t_sol_count *result)
{
	int	digit;

	*result = 1;
	if (!str)
		return (1);
	if (!*str)
		return (0);
	*result = 0;
	while (*str >= '0' && *str <= '9')
	{
		digit = *str - '0';
		if (*result > (MAX_SOL_COUNT - digit) / 10)
			return (0);
		*result = 10 * *result + digit;
		str++;
	}
	return (*str == '\0');
}

int	init_puzzle_from_constr_str(t_solver_state *puzzle, char *str,
		char *max_sol)
{
	int			size;
	t_sol_count	max_solutions;

	puzzle->solutions = (0);
	if (!parse_max_solution(max_sol, &max_solutions))
		return (0);
	size = parse_puzzle_size_from_constr_str(str);
	if (!size || !init_puzzle(puzzle, size, max_solutions))
		return (0);
	return (try_add_constr_values(puzzle, str));
}

int	set_puzzle_grid_to_str_vals(t_solver_state *puzzle, char *str)
{
	int		idx;
	int		new_val;

	idx = 0;
	while (str[idx] && idx / 2 < puzzle->squared_size)
	{
		if (idx % 2 == 0)
		{
			new_val = str[idx] - '0';
			if (new_val < 0 || new_val > puzzle->size)
				return (0);
			puzzle->cur_node->domain.vals[idx / 2] = new_val;
		}
		else if (str[idx] != ' ')
			return (0);
		idx++;
	}
	return (!str[idx] && (idx + 1) == 2 * puzzle->squared_size);
}

static int	parse_puzzle_size_from_constr_str(char *str)
{
	int		space_expected;
	int		counter;

	counter = 0;
	space_expected = 0;
	while (*str)
	{
		if (space_expected && *str != ' ')
			return (0);
		else if (!space_expected && (*str < '0' || *str > '9'))
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

static int	try_add_constr_values(t_solver_state *puzzle, char *str)
{
	int		word_idx;
	int		pair_idx;
	int		val;
	int		size;

	size = puzzle->size;
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
