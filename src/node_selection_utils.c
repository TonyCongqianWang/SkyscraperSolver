/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_utils.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/10 11:02:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/10 11:02:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_eval.h"

int	get_cache_index(t_node_state *node)
{
	if (node->is_in_lookahead_select && node->sub_node_depth == 0)
		return (2);
	if (node->sub_node_depth == 0)
		return (0);
	return (1);
}

int	check_sel(t_node_state *node, int idx, t_node_select_config *conf)
{
	int	r;
	int	c;

	if (!node->is_in_lookahead_select || !conf->is_selective)
		return (1);
	r = idx / node->size;
	c = idx % node->size;
	return ((node->rows_changed_since_prune & (1 << r))
		|| (node->cols_changed_since_prune & (1 << c)));
}

void	init_node_transition(t_node_transition *tr)
{
	tr->cell_idx = -1;
	tr->cell_val = 1;
	tr->score = 0.0;
	tr->num_valids_col = 0;
	tr->num_valids_row = 0;
	tr->num_valids_cell = 0;
}
