/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_root.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_root.h"
#include "prune_strat_root_helpers.h"
#include "pruning_routines.h"
#include "pruning_configs.h"
#include "entropy.h"
#include "math_utils.h"
#include "params_int.h"
#include "params_double.h"

static int	run_tier_complement(t_puzzle *puzzle, int remaining_entropy)
{
	t_prune_routine_cfg	cfg;

	get_prune_cfg_complement(&cfg);
	cfg.lookahead.check_mode.run_constr = 1;
	cfg.lookahead.check_mode.run_gac = 1;
	cfg.lookahead.check_mode.run_prop = 1;
	cfg.lookahead.check_mode.lookahead_continue_min_entropy
		= g_root_lookahead_continue_min_entropy;
	cfg.lookahead.check_mode.lookahead_continue_slope
		= g_root_lookahead_continue_slope;
	setup_cfg_bounds(&cfg, puzzle->cur_node->num_unset, puzzle->size);
	(void)remaining_entropy;
	return (run_pruning_routine(puzzle, &cfg, 3));
}

static int	run_tier(t_puzzle *puzzle, int tier, int remaining_entropy)
{
	t_prune_routine_cfg	cfg;

	if (tier == 0)
		get_prune_cfg_light(&cfg);
	else if (tier == 1)
		get_prune_cfg_medium(&cfg);
	else
		get_prune_cfg_heavy(&cfg);
	setup_cfg_thresholds(&cfg, remaining_entropy);
	setup_cfg_bounds(&cfg, puzzle->cur_node->num_unset, puzzle->size);
	return (run_pruning_routine(puzzle, &cfg, tier));
}

static double	calc_period(t_puzzle *puzzle, t_node_state *node)
{
	double	raw;
	int		rem;

	rem = node->remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem) / rem;
	return (g_root_period_coef_scale * dpow075_approx(raw)
		+ g_root_period_coef_unset
		* (puzzle->squared_size - node->num_unset));
}

int	prune_strat_root(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			period;
	int				pruned;

	node = puzzle->cur_node;
	if (node->is_invalid || node->is_complete || node->num_unset == 0
		|| node->remaining_entropy < g_root_min_entropy)
		return (0);
	period = calc_period(puzzle, node);
	pruned = 0;
	if (node->last_entropy[0] - node->remaining_entropy > period)
		pruned = run_tier(puzzle, 0, node->remaining_entropy);
	else if (node->last_entropy[1] - node->remaining_entropy
		> period * g_root_period_tier_medium_mult)
		pruned = run_tier(puzzle, 1, node->remaining_entropy);
	else if (node->last_entropy[2] - node->remaining_entropy
		> period * g_root_period_tier_heavy_mult)
		pruned = run_tier(puzzle, 2, node->remaining_entropy);
	if (pruned)
		return (1);
	if (node->last_entropy[3] - node->remaining_entropy
		> period * g_root_period_tier_complement_mult)
		return (run_tier_complement(puzzle, node->remaining_entropy));
	return (0);
}
