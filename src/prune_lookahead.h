/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_lookahead.h                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PRUNE_LOOKAHEAD_H
# define PRUNE_LOOKAHEAD_H

# include "puzzle_structs.h"
# include "strategy_config.h"

typedef enum e_lookahead_pass
{
	LOOKAHEAD_PASS_NONE = 0,
	LOOKAHEAD_PASS_POS = 1 << 0,
	LOOKAHEAD_PASS_NEG = 1 << 1,
	LOOKAHEAD_PASS_BOTH = LOOKAHEAD_PASS_POS | LOOKAHEAD_PASS_NEG
}	t_lookahead_pass;

void	prune_lookahead(t_puzzle *puzzle, t_lookahead_config *config);
void	run_lookahead_loop(t_puzzle *puzzle, t_node_state *node,
			const t_lookahead_config *config);
void	run_lookahead_transitions(t_puzzle *puzzle,
			t_node_transition *tr, const t_lookahead_config *config,
			t_lookahead_pass passes);

#endif
