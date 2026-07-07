/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_deep.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_deep.h"
#include "pruning_routines.h"

static const double	g_min_unset_threshold = 0.144440768499286;
static const double	g_gac_unset_threshold = 0.241505401466146;
static const double	g_constr_min_unset = 0.497582762441804;
static const double	g_constr_max_unset = 0.536472818366295;
static const double	g_lookahead_gac_unset_threshold = 0.241505401466146;
static const double	g_lookahead_constr_min_unset = 0.497582762441804;
static const double	g_lookahead_constr_max_unset = 0.536472818366295;
static const double	g_lookahead_downgrade_fraction = 0.05;
static const int	g_period_base = 237;
static const int	g_period_coef1 = 11107;
static const int	g_period_coef2 = 85321;

static int	run_tier(t_puzzle *puzzle, int tier, double unset_ratio)
{
	t_prune_routine_cfg	cfg;

	if (tier == 0)
		get_prune_cfg_light(&cfg);
	else if (tier == 1)
		get_prune_cfg_medium(&cfg);
	else
		get_prune_cfg_heavy(&cfg);
	cfg.run_gac = (unset_ratio >= g_gac_unset_threshold);
	cfg.run_check_constr = (unset_ratio >= g_constr_min_unset
			&& unset_ratio <= g_constr_max_unset);
	cfg.lookahead.check_mode.run_constr = 1;
	cfg.lookahead.check_mode.run_gac = (unset_ratio
			>= g_lookahead_gac_unset_threshold);
	cfg.lookahead.check_mode.run_prop = (unset_ratio
			>= g_lookahead_constr_min_unset
			&& unset_ratio <= g_lookahead_constr_max_unset);
	cfg.lookahead.check_mode.downgrade_fraction
		= g_lookahead_downgrade_fraction;
	return (run_pruning_routine(puzzle, &cfg, tier));
}

int	prune_strat_deep(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			unset_ratio;
	double			x;
	t_prune_prog	period;

	node = puzzle->cur_node;
	if (node->is_invalid || node->is_complete || node->num_unset == 0)
		return (0);
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	if (unset_ratio < g_min_unset_threshold)
		return (0);
	x = 1 - unset_ratio;
	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);
	if (node->progress_counter > node->last_prog[0] + period / 2)
		return (run_tier(puzzle, 0, unset_ratio));
	if (node->progress_counter > node->last_prog[1] + period)
		return (run_tier(puzzle, 1, unset_ratio));
	if (node->progress_counter > node->last_prog[2] + period * 2)
		return (run_tier(puzzle, 2, unset_ratio));
	return (0);
}
