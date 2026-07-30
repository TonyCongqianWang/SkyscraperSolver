/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   cell_distance.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:40:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:40:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "puzzle_init.h"
#include "cell_distance.h"

static int	get_cell_dist_val(int idx, int size)
{
	int		x_edge_dist;
	int		y_edge_dist;
	int		score_component;
	int		s;

	x_edge_dist = idx % size;
	if (x_edge_dist > size / 2)
		x_edge_dist = size - x_edge_dist;
	y_edge_dist = idx / size;
	if (y_edge_dist > size / 2)
		y_edge_dist = size - y_edge_dist;
	s = size + 1;
	score_component = s * s;
	if (x_edge_dist <= y_edge_dist)
		score_component -= x_edge_dist * s + y_edge_dist;
	else
		score_component -= y_edge_dist * s + x_edge_dist;
	return (score_component);
}

static void	init_scores(t_puzzle *puzzle, int *temp_scores, int size)
{
	int	i;

	i = 0;
	while (i < puzzle->squared_size)
	{
		puzzle->cell_distance_order[i] = i;
		temp_scores[i] = get_cell_dist_val(i, size);
		i++;
	}
}

static void	sort_cell_order(t_puzzle *puzzle, int *temp_scores)
{
	int	i;
	int	j;
	int	key;
	int	key_score;

	i = 1;
	while (i < puzzle->squared_size)
	{
		key = puzzle->cell_distance_order[i];
		key_score = temp_scores[key];
		j = i - 1;
		while (j >= 0)
		{
			if (temp_scores[puzzle->cell_distance_order[j]] >= key_score)
				break ;
			puzzle->cell_distance_order[j + 1]
				= puzzle->cell_distance_order[j];
			j--;
		}
		puzzle->cell_distance_order[j + 1] = key;
		i++;
	}
}

void	init_cell_distance_order(t_puzzle *puzzle, int size)
{
	int	temp_scores[MAX_CELL_COUNT];

	init_scores(puzzle, temp_scores, size);
	sort_cell_order(puzzle, temp_scores);
}
