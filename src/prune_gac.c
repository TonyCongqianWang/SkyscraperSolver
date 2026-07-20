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
#include "selectivity.h"
#include "grid_interface.h"
#include "check_node_validity.h"
#include "entropy.h"

static int	collect_line_cells(t_node_state *state, int line_idx, int is_col,
				int *cells)
{
	int	count;
	int	i;
	int	cell;

	count = 0;
	i = 0;
	while (i < state->size)
	{
		if (is_col)
			cell = i * state->size + line_idx;
		else
			cell = line_idx * state->size + i;
		if (is_cell_empty(state, cell))
		{
			cells[count] = cell;
			count++;
		}
		i++;
	}
	return (count);
}

static void	run_gac_analysis_line(t_puzzle *puzzle, int *cells, int count,
				t_gac_config *config)
{
	t_gac_batch	batch;
	int			i;

	batch.state = puzzle->cur_node;
	batch.update_count = 0;
	i = 0;
	while (i < MAX_CELL_COUNT)
		batch.pruned_masks[i++] = 0;
	if (config->analyse_naked)
		run_gac_naked(cells, count, config, &batch);
	if (config->analyse_hidden)
		run_gac_hidden(cells, count, config, &batch);
	if (batch.update_count > 0)
		set_cells_invalid_batch(puzzle, batch.updates, batch.update_count,
			g_check_none);
}

void	analyse_gac_line(t_puzzle *puzzle, int idx, int is_col,
			t_gac_config *config)
{
	int		cells[MAX_SIZE];
	int		count;
	int		constr_idx;
	double	local_ratio;

	if (puzzle->cur_node->remaining_entropy < config->global_min_entropy)
		return ;
	if (is_col)
		constr_idx = idx;
	else
		constr_idx = idx + puzzle->cur_node->size;
	local_ratio = get_relative_constr_entropy(puzzle->cur_node, constr_idx,
			puzzle->cur_node->size);
	if (local_ratio < config->min_unset || local_ratio > config->max_unset)
		return ;
	count = collect_line_cells(puzzle->cur_node, idx, is_col, cells);
	run_gac_analysis_line(puzzle, cells, count, config);
}

void	prune_gac(t_puzzle *puzzle, t_gac_config *config)
{
	t_node_state	*state;
	int				i;

	state = puzzle->cur_node;
	if (should_exit_selectivity(state, config->selectivity))
		return ;
	i = 0;
	while (i < state->size)
	{
		if (should_process_row(state, i, config->selectivity))
			analyse_gac_line(puzzle, i, 0, config);
		i++;
	}
	i = 0;
	while (i < state->size)
	{
		if (should_process_col(state, i, config->selectivity))
			analyse_gac_line(puzzle, i, 1, config);
		i++;
	}
	check_node_validity(puzzle, g_check_constr);
}
