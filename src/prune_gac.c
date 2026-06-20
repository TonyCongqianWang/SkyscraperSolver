/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_gac.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:57:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:57:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_gac.h"
#include "prune_gac_naked.h"
#include "prune_gac_hidden.h"
#include "prune_gac_domain.h"
#include "grid_availability.h"

static int	collect_row_cells(t_node_state *state, int r, int *cells)
{
	int	count;
	int	c;

	count = 0;
	c = 0;
	while (c < state->size)
	{
		if (is_cell_empty(state, r * state->size + c))
		{
			cells[count] = r * state->size + c;
			count++;
		}
		c++;
	}
	return (count);
}

static int	collect_col_cells(t_node_state *state, int col, int *cells)
{
	int	count;
	int	r;

	count = 0;
	r = 0;
	while (r < state->size)
	{
		if (is_cell_empty(state, r * state->size + col))
		{
			cells[count] = r * state->size + col;
			count++;
		}
		r++;
	}
	return (count);
}

static void	analyse_row(t_node_state *state, int r, t_gac_config *config)
{
	int	cells[MAX_SIZE];
	int	val_cells[MAX_SIZE];
	int	count;

	count = collect_row_cells(state, r, cells);
	if (config->analyse_naked)
	{
		if (config->max_k >= 2)
			analyse_naked_pairs(state, cells, count);
		if (config->max_k >= 3)
			analyse_naked_triples(state, cells, count);
	}
	if (config->analyse_hidden)
	{
		get_value_cells(state, cells, count, val_cells);
		if (config->max_k >= 2)
			analyse_hidden_pairs(state, cells, count, val_cells);
		if (config->max_k >= 3)
			analyse_hidden_triples(state, cells, count, val_cells);
	}
}

static void	analyse_col(t_node_state *state, int col, t_gac_config *config)
{
	int	cells[MAX_SIZE];
	int	val_cells[MAX_SIZE];
	int	count;

	count = collect_col_cells(state, col, cells);
	if (config->analyse_naked)
	{
		if (config->max_k >= 2)
			analyse_naked_pairs(state, cells, count);
		if (config->max_k >= 3)
			analyse_naked_triples(state, cells, count);
	}
	if (config->analyse_hidden)
	{
		get_value_cells(state, cells, count, val_cells);
		if (config->max_k >= 2)
			analyse_hidden_pairs(state, cells, count, val_cells);
		if (config->max_k >= 3)
			analyse_hidden_triples(state, cells, count, val_cells);
	}
}

void	prune_gac(t_puzzle *puzzle, t_gac_config *config)
{
	t_node_state	*state;
	int				i;

	state = puzzle->cur_node;
	i = 0;
	while (i < state->size)
	{
		if (config->selectivity == SELECTIVITY_NONE
			|| (state->rows_changed_since_prune & (1 << i))
			|| (config->selectivity == SELECTIVITY_ANY_CHANGE
				&& (state->rows_invalid_since_prune & (1 << i))))
			analyse_row(state, i, config);
		if (config->selectivity == SELECTIVITY_NONE
			|| (state->cols_changed_since_prune & (1 << i))
			|| (config->selectivity == SELECTIVITY_ANY_CHANGE
				&& (state->cols_invalid_since_prune & (1 << i))))
			analyse_col(state, i, config);
		i++;
	}
}
