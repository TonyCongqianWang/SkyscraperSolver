/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   selectivity_line.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:40:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:40:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "selectivity.h"

int	should_process_line(const t_node_state *state, int idx,
			t_selectivity_level selectivity)
{
	if (idx < state->size)
		return (should_process_col(state, idx, selectivity));
	return (should_process_row(state, idx - state->size, selectivity));
}
