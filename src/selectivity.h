/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   selectivity.h                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/26 13:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef SELECTIVITY_H
# define SELECTIVITY_H

# include "puzzle_structs.h"
# include "strategy_config.h"

int	should_exit_selectivity(const t_node_state *node,
		t_selectivity_level selectivity);
int	should_process_row(const t_node_state *state, int r,
		t_selectivity_level selectivity);
int	should_process_col(const t_node_state *state, int c,
		t_selectivity_level selectivity);

#endif
