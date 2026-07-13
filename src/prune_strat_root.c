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
#include "pruning_routines.h"

static const double	g_min_unset_threshold = 0.186839988330004;
static const double	g_gac_min_unset = 0.105152884234497;
static const double	g_constr_min_unset = 0.0231762279198338;
static const double	g_lookahead_downgrade_fraction = 0.0529394833310167;
static const int	g_period_base = 6;
static const int	g_period_coef1 = 2563;
static const int	g_period_coef2 = 26552;
static const double	g_gac_local_min_unset = 0.1;
static const double	g_gac_local_max_unset = 0.85;
static const double	g_gac_global_min_unset = 0.476410263363036;
static const double	g_constr_local_min_unset = 0.1;
static const double	g_constr_local_max_unset = 0.85;
static const double	g_constr_global_min_unset = 0.531086476103288;
static const double	g_lookahead_gac_local_min_unset = 0.1;
static const double	g_lookahead_gac_local_max_unset = 0.85;
static const double	g_lookahead_gac_global_min_unset = 0.535956651893916;
static const double	g_lookahead_constr_local_min_unset = 0.1;
static const double	g_lookahead_constr_local_max_unset = 0.85;
static const double	g_lookahead_constr_global_min_unset = 0.473393654677003;

static void	setup_cfg_thresholds(t_prune_routine_cfg *cfg, double unset_ratio)
{
	cfg->run_gac = (unset_ratio >= g_gac_min_unset);
	cfg->run_check_constr = (unset_ratio >= g_constr_min_unset);
	cfg->lookahead.check_mode.run_constr = 1;
	cfg->lookahead.check_mode.run_gac = 1;
	cfg->lookahead.check_mode.run_prop = 1;
	cfg->lookahead.check_mode.downgrade_fraction
		= g_lookahead_downgrade_fraction;
}

static void	setup_cfg_bounds(t_prune_routine_cfg *cfg)
{
	cfg->gac.min_unset = g_gac_local_min_unset;
	cfg->gac.max_unset = g_gac_local_max_unset;
	cfg->gac.global_min_unset = g_gac_global_min_unset;
	cfg->check_constr_min_unset = g_constr_local_min_unset;
	cfg->check_constr_max_unset = g_constr_local_max_unset;
	cfg->check_constr_global_min_unset
		= g_constr_global_min_unset;
	cfg->lookahead.check_mode.constr.min_unset
		= g_lookahead_constr_local_min_unset;
	cfg->lookahead.check_mode.constr.max_unset
		= g_lookahead_constr_local_max_unset;
	cfg->lookahead.check_mode.constr.global_min_unset
		= g_lookahead_constr_global_min_unset;
	cfg->lookahead.check_mode.gac.min_unset
		= g_lookahead_gac_local_min_unset;
	cfg->lookahead.check_mode.gac.max_unset
		= g_lookahead_gac_local_max_unset;
	cfg->lookahead.check_mode.gac.global_min_unset
		= g_lookahead_gac_global_min_unset;
}

static int	run_tier(t_puzzle *puzzle, int tier, double unset_ratio)
{
	t_prune_routine_cfg	cfg;

	if (tier == 0)
		get_prune_cfg_light(&cfg);
	else if (tier == 1)
		get_prune_cfg_medium(&cfg);
	else
		get_prune_cfg_heavy(&cfg);
	setup_cfg_thresholds(&cfg, unset_ratio);
	setup_cfg_bounds(&cfg);
	return (run_pruning_routine(puzzle, &cfg, tier));
}

int	prune_strat_root(t_puzzle *puzzle)
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
